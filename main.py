import cellmap
import player
import entity
import event
import colors
import logging
log = logging.getLogger()
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
#sh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s'))
log.addHandler(sh)
log.setLevel(logging.INFO)
log.debug("Started logger")


colors.cprint("Loading map...\n")
m = cellmap.Map()
m.gen(10)

pc = player.Player()
#pc.level_up(5)
pc.weapon = entity.Weapon("Super Sword").power(12035)
entity.player_uuid = pc.uuid
here = m.grid[pc.pos]
colors.cprint("Done!\n")

def main():
    global here
    while True:
        here = m.grid[pc.pos]
        print(pc.pos)
        print(m.show2d(*pc.pos))
        print(here.look())
        dirs = list(m.get_dirs(*pc.pos))
        names = map(lambda x: cellmap.dir_name(*x), dirs)
        colors.cprint(", ".join(names)+"\n", color=colors.OKGREEN)
        read_command()

def go(v):
    dirs = list(m.get_dirs(*pc.pos))
    choice = cellmap.d2n(v)
    if choice in dirs:
        pc.go_dir(choice)
    else:
        badcmd("can't go that way ({})\n".format(choice))

def get(v):
    t = target(v, cls=entity.Item)
    if t:
        pc.get(t)
        here.remove(t)
        pcprint("You pick up {}\n".format(t))
        event.log("player.action.get")
    else:
        if v:
            badcmd("I don't see {} here\n".format(v))
        else:
            badcmd("There's nothing to get\n")

def attack(v):
    t = target(v, cls=entity.Character)
    if t:
        pc.attack(t)
        event.log("player.action.attack")
    else:
        badcmd("Who?\n")

def equip(v):
    t = target(v, cls=entity.Weapon, inv=True)
    if t:
        pc.equip(t)
        event.log("player.action.equip")
    else:
        badcmd("Equip what?\n")

def unequip(v):
    if pc.weapon:
        pc.unequip()
        event.log("player.action.unequip")
    else:
        badcmd("You're not holding a weapon\n")

def drop(v):
    if pc.weapon and pc.weapon.name.upper() == v:
        pc.unequip()
    t = target(v, inv=True)
    if t:
        pc.drop(t)
        event.log("player.action.drop")
    else:
        badcmd("Drop what?\n")

def look_self(v):
    pcprint(pc.look()+"\n")

def look(v):
    t = target(v)
    if t:
        pcprint(t.look()+"\n")
    else:
        badcmd("At what?\n")

def target(name, cls=None, inv=None):
    if inv:
        loc = pc.inv
    else:
        loc = m.grid[pc.pos].entities
    if cls:
        ents = list(e for e in loc if isinstance(e, cls))
    else:
        ents = list(e for e in loc)

    if len(ents) == 0:
        return False
    elif len(ents) == 1:
        return ents[0]
    elif name:
        for e in ents:
            if name in e.name.upper():
                return e
        return False
    else:
        return False



@event.on("player.action")
def main_ai(kwg):
    # do encounters
    ents = {e.uuid: True for e in m.grid[pc.pos].entities}
    event._log(event.Event("player.encounter", ents))

@event.on("character.inventory.drop")
def dropped_item(kwg):
    m.grid[kwg['pos']].entities.append(kwg['item'])

@event.on("combat.damage")
def clog_damage(kwg):
    sub = entity.all_entities[kwg['sub']]
    hprint("{}: Ouch! (-{} HP)\n".format(sub.name, kwg['amount']))

@event.on("combat.attack")
def clog_attack(kwg):
    sub = entity.all_entities[kwg['sub']]
    obj = entity.all_entities[kwg['obj']]
    hprint("{} attacks {}!\n".format(sub, obj))

def pcprint(msg):
    colors.cprint(msg, color=colors.OKBLUE)

def badcmd(msg):
    colors.cprint(msg, color=colors.WARNING)

def hprint(msg):
    colors.cprint(msg, color=colors.FAIL)


def cmdhelp(v):
    msg = "Possible commands are:\n"
    msg += "\n".join(commands.keys())
    msg += "\n"
    colors.cprint(msg, color=colors.WARNING)

commands = {
    'GO': go,
    'GET': get,
    'ATTACK': attack,
    'SELF': look_self,
    'LOOK': look,
    'EQUIP': equip,
    'DROP': drop,
    'UNEQUIP': unequip,
    'QUIT': quit,
    'HELP': cmdhelp
}

def read_command():
    v = raw_input("> ").upper().split(' ', 1)
    if v[0] in commands:
        if len(v) > 1:
            commands[v[0]](v[1:][0])
        else:
            commands[v[0]](None)
    else:
        badcmd("I don't understand that command\n")

main()
