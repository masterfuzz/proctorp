import random
import event
import uuid

all_entities = {}
player_uuid = None

class Entity(object):
    def __init__(self, name="<Unknown>"):
        self.name = name
        self.phys = True
        self.ai = False
        self.uuid = uuid.uuid1()
        all_entities[self.uuid] = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

    def look(self):
        return self.name

class LeveledEntity(Entity):
    def __init__(self, name="<Unknown>", level=1):
        self.lvl = level
        super(LeveledEntity,self).__init__(name)

    def look(self):
        return str(self)

    def level(self, level):
        self.lvl = level
        return self

    def level_up(self, to):
        by = to - self.lvl
        self.lvl = to
        #print("{} leveled up!".format(self))
        for k, x in self.__dict__.items():
            if isinstance(x, Attrib):
                x.level_up(by)
                print("{}: {}".format(k,x))

        return self

    def __str__(self):
        return "Level {} {}".format(self.lvl, self.name)

class Item(LeveledEntity):
    def look(self):
        return "A Level {} {}".format(self.lvl, self.name)

class Treasure(Item):
    def __init__(self, name="Treasure", level=1):
        self.items = []
        super(Treasure,self).__init__(name, level)

    def add(self, *items):
        self.items += items
        return self

class Weapon(Item):
    def __init__(self, name, level=1):
        self.pwr = 1
        super(Weapon, self).__init__(name, level)

    def power(self, power):
        self.pwr = power
        return self

    def level_up(self, to):
        self.power += to - self.lvl
        return self

    def look(self):
        return super(Weapon,self).look() + "\nPower: {}".format(self.pwr)

class Attrib:
    def __init__(self, val, growth=5):
        self.min = 0
        self.val = val
        self.max = val
        self.growth = growth
        self.uuid = uuid.uuid1()

    def full(self):
        return self.val == self.max

    def level_up(self, by):
        self.val += by * self.growth
        self.max += by * self.growth

    def __str__(self):
        return "{}/{}".format(self.val, self.max)

    def __repr__(self):
        return "Attrib({},{},{},{})".format(self.min,
                                            self.val,
                                            self.max,
                                            self.growth)

    @event.trigger("attribute.value.changed")
    def damage(self, v):
        self.val = max(self.min, self.val - v)
        return {'target': self.uuid, 'new_value': self.val}

    @event.trigger("attribute.value.changed")
    def heal(self, v):
        self.val = min(self.max, self.val + v)
        return {'target': self.uuid, 'new_value': self.val}

class Character(LeveledEntity):
    def __init__(self, name, level=1):
        super(Character,self).__init__(name,level)
        self.hp = Attrib(10 * level, 10)
        self.st = Attrib(5 * level, 5)
        self.df = Attrib(5 * level, 5)
        self.xp = Attrib(100 * level, 100)
        self.weapon = None
        self.ai_hostile = False
        self.dead = False
        self.inv = []

        event.when("combat.attack", {'target': self.uuid})(self.attacked)
        event.when("attribute.value.changed", {'target': self.hp.uuid,
                                               'new_value': 0})(self.die)

    @event.trigger("character.inventory.get")
    def get(self, item):
        self.inv.append(item)
        return {'target': item.uuid, 'source': self.uuid}

    def die(self, kwargs):
        if not self.dead:
            print("{} died!".format(self.name))
            self.dead = True
            event.log("character.death", target=self.uuid)

    def __str__(self):
        dstr = ", dead" if self.dead else ""
        return "{} (Level {}{})".format(self.name, self.lvl, dstr)

    def look(self):
        desc = str(self) + "\n"
        if self.ai_hostile:
            desc += "Hostile\n"
        for k,v in self._attribs().items():
            if v.full():
                desc += "{}: {}\n".format(k, v.val)
            else:
                desc += "{}: {}/{}\n".format(k, v.val, v.max)
        desc += "Weilding: {}\n".format(self.weapon)
        if self.inv:
            desc += "Inventory: " + ", ".join(map(str, self.inv)) + "\n"
        return desc

    def _attribs(self):
        return {k: v for k,v in self.__dict__.items() if isinstance(v, Attrib)}

    def hostile(self, yes=True):
        self.ai_hostile = yes
        return self

    def take_dmg(self, dmg):
        print("{}: Ouch! (-{} HP)".format(self.name, dmg))
        self.hp.damage(dmg)
        return self

    @event.trigger("combat.attack")
    def attack(self, target):
        if self.dead:
            print("{} can't attack! (dead)".format(self.name))
            return {'_block': True}
        if isinstance(target, Entity):
            target = target.uuid
        return {'source': self.uuid, 'target': target, 'damage': self.deal_melee()}

    def attacked(self, kwargs):
        self.take_dmg(kwargs.get('damage',0))
        if self.ai_hostile and not self.dead:
            self.attack(kwargs['source'])

    def deal_melee(self):
        if self.weapon:
            return self.st.val + self.weapon.pwr
        else:
            return self.st.val

    def equip(self, w):
        self.weapon = w
        return self

class NPC(Character):
    def __init__(self, name, level=1):
        super(NPC,self).__init__(name, level)
        self.prompts = {}
        self.unprompts = []

        event.when("player.encounter", {self.uuid: True})(self.say)

    def dialog(self, txt, prompt=None):
        if prompt:
            self.prompts[prompt] = txt
        else:
            self.unprompts.append(txt)
        return self

    def say(self, k):
        if self.unprompts:
            print("{}: {}".format(self.name, random.choice(self.unprompts)))
        else:
            print("{}: ...".format(self.name))

class MOB(Character):
    def __init__(self, name, level=1):
        super(MOB,self).__init__(name,level)
        self.ai_hostile = False

        event.when("player.encounter", {self.uuid: True})(self.on_encounter)

    def on_encounter(self, k):
        if not self.dead:
            self.attack(player_uuid)

@event.on("combat.attack")
def combat_log_attack(k):
    global all_entities
    sub = all_entities[k['source']]
    obj = all_entities[k['target']]
    print("{} attacked {}!".format(sub, obj))

