import cellmap
import player
import entity
import event
import logging
log = logging.getLogger()
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
#sh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s'))
log.addHandler(sh)
log.setLevel(logging.INFO)
log.debug("Started logger")


m = cellmap.Map()
m.gen(10)

pc = player.Player()
pc.level_up(5)
entity.player_uuid = pc.uuid
here = m.grid[pc.pos]

def main():
    global here
    while True:
        here = m.grid[pc.pos]
        print(pc.pos)
        print(m.show2d(*pc.pos))
        print(here.look())
        dirs = list(m.get_dirs(*pc.pos))
        names = map(lambda x: cellmap.dir_name(*x), dirs)
        print(", ".join(names))
        read_command()

def go(v):
    dirs = list(m.get_dirs(*pc.pos))
    choice = cellmap.d2n(v)
    if choice in dirs:
        pc.go_dir(choice)
    else:
        print("can't go that way ({})".format(choice))

def get(v):
    t = target(v, cls=entity.Item)
    if t:
        pc.get(t)
        here.remove(t)
        print("You pick up {}".format(t))
        event.log("player.action.get")
    else:
        if v:
            print("I don't see {} here".format(v))
        else:
            print("There's nothing to get")

def attack(v):
    t = target(v, cls=entity.Character)
    if t:
        pc.attack(t)
        event.log("player.action.attack")
    else:
        print("Who?")

def look_self(v):
    print(pc.look())

def look(v):
    t = target(v)
    if t:
        print(t.look())
    else:
        print("At what?")

def target(name, cls=None):
    if cls:
        ents = list(e for e in m.grid[pc.pos].entities if isinstance(e, cls))
    else:
        ents = list(e for e in m.grid[pc.pos].entities)

    if len(ents) == 0:
        return False
    elif len(ents) == 1:
        return ents[0]
    else:
        for e in ents:
            if name in e.name.upper():
                return e
        return False

commands = {
    'GO': go,
    'GET': get,
    'ATTACK': attack,
    'SELF': look_self,
    'LOOK': look
}

def read_command():
    v = raw_input("> ").upper().split(' ', 1)
    if v[0] in commands:
        if len(v) > 1:
            commands[v[0]](v[1:][0])
        else:
            commands[v[0]](None)
    else:
        print("wat")

@event.on("player.action")
def main_ai(kwg):
    # do encounters
    ents = {e.uuid: True for e in m.grid[pc.pos].entities}
    event._log(event.Event("player.encounter", ents))

@event.on("character.inventory.drop")
def dropped_item(kwg):
    m.grid[kwg['pos']].entities.append(kwg['item'])

main()
