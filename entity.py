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
        self.pos = (0,0,0)
        self.tags = set((self.name,))

    def tag(self, tag):
        self.tags.add(tag)
        return self

    def untag(self, tag):
        self.tags.remove(tag)
        return self

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

    def look(self):
        return self.name

class LeveledEntity(Entity):
    def __init__(self, name="<Unknown>", level=1):
        super(LeveledEntity,self).__init__(name)
        self.level(level)

    def look(self):
        return str(self)

    @event.trigger("entity.xp.gain")
    def gain_xp(self, amt):
        self.xp += amt
        lvl = self.lvl
        while 100*(2**(lvl-1)) < self.xp:
            lvl+=1
        if lvl > self.lvl:
            self.level_up(lvl)
        return {'sub': self.uuid, 'amount': amt}

    def level(self, level):
        self.lvl = level
        self.xp = 100*(2**(level-2))
        return self

    def level_up(self, to):
        by = to - self.lvl
        self.level(to)
        for k, x in self.__dict__.items():
            if isinstance(x, Attrib):
                x.level_up(by)

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
        return {'obj': self.uuid, 'new_value': self.val}

    @event.trigger("attribute.value.changed")
    def heal(self, v):
        self.val = min(self.max, self.val + v)
        return {'obj': self.uuid, 'new_value': self.val}

class Character(LeveledEntity):
    def __init__(self, name, level=1):
        super(Character,self).__init__(name,level)
        self.hp = Attrib(10 * level, 10)
        self.st = Attrib(5 * level, 5)
        self.df = Attrib(5 * level, 5)
        self.weapon = None
        self.ai_hostile = False
        self.ai_neutral = True # becomes hostile
        self.dead = False
        self.inv = []
        self.last_hit = None

        event.when("combat.attack", {'obj': self.uuid})(self.attacked)
        event.when("attribute.value.changed", {'obj': self.hp.uuid,
                                               'new_value': 0})(self.die)
        event.when("character.death", {'last_hit': self.uuid})(self.combat_xp)

    @event.trigger("character.inventory.get")
    def get(self, item):
        self.inv.append(item)
        return {'obj': item.uuid, 'sub': self.uuid}


    def die(self, kwargs):
        if not self.dead:
            self.drop_all()
            print("{} died!".format(self.name))
            self.dead = True
            event.log("character.death", sub=self.uuid, last_hit=self.last_hit)

    def combat_xp(self, k):
        if self.dead:
            return
        # xp gain = level * 50
        e = all_entities[k['sub']]
        self.gain_xp(e.lvl * 50)

    def drop_all(self):
        self.unequip()
        for i in self.inv:
            event.log("character.inventory.drop", item=i, pos=self.pos)
        self.inv = []

    def drop(self, item):
        for i,v in enumerate(self.inv):
            if item.uuid == v.uuid:
                del self.inv[i]
                event.log("character.inventory.drop", item=item, pos=self.pos)
                return

    # remove without dropping
    def remove_item(self, item):
        for i,v in enumerate(self.inv):
            if item.uuid == v.uuid:
                del self.inv[i]
                return

    @event.trigger("character.inventory.equip")
    def equip(self, i):
        if self.weapon:
            self.unequip()
        self.weapon = i
        self.remove_item(i)
        return {'sub': self.uuid, 'obj': i.uuid}

    @event.trigger("character.inventory.unequip")
    def unequip(self):
        if self.weapon:
            wpn = self.weapon
            self.inv.append(wpn)
            self.weapon = None
            return {'sub': self.uuid, 'obj': wpn}
        else:
            return {'_block': True}

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
        desc += "{}/{} XP\n".format(self.xp, 100*(2**(self.lvl-1)))
        desc += "Weilding: {}\n".format(self.weapon)
        if self.inv:
            desc += "Inventory: " + ", ".join(map(str, self.inv)) + "\n"
        return desc

    def _attribs(self):
        return {k: v for k,v in self.__dict__.items() if isinstance(v, Attrib)}

    def hostile(self, yes=True):
        self.ai_hostile = yes
        return self

    @event.trigger("combat.damage")
    def take_dmg(self, dmg):
        dmg = max(1, dmg - self.df.val)
        self.hp.damage(dmg)
        return {'sub': self.uuid, 'amount': dmg}

    @event.trigger("combat.attack")
    def attack(self, obj):
        if self.dead:
            print("{} can't attack! (dead)".format(self.name))
            return {'_block': True}
        if isinstance(obj, Entity):
            obj = obj.uuid
        return {'sub': self.uuid, 'obj': obj, 'damage': self.deal_melee()}

    def attacked(self, kwargs):
        if not self.dead:
            self.last_hit = kwargs.get('sub')
            self.take_dmg(kwargs.get('damage',0))
            if self.ai_neutral:
                self.ai_hostile = True

    def deal_melee(self):
        if self.weapon:
            return self.st.val + self.weapon.pwr
        else:
            return self.st.val

    def wielding(self, w):
        self.weapon = w
        return self

class NPC(Character):
    def __init__(self, name, level=1):
        super(NPC,self).__init__(name, level)
        self.prompts = {}
        self.unprompts = []

        event.when("player.encounter", {self.uuid: True})(self.say)

    def quest(self, give_txt, quest, compl_txt):
        return self

    def dialog(self, txt, prompt=None):
        if prompt:
            self.prompts[prompt] = txt
        else:
            self.unprompts.append(txt)
        return self

    def say(self, k):
        if self.dead:
            return
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

