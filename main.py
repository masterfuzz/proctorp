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
log.setLevel(logging.DEBUG)
log.debug("Started logger")


m = cellmap.Map()
m.gen(10)

pc = player.Player()
pc.level_up(5)
entity.player_uuid = pc.uuid

def main():
    while True:
        print(pc.pos)
        print(m.show2d(*pc.pos))
        print(m.grid[pc.pos].look())
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
    print("not yet")

def attack(v):
    ents = list(e for e in m.grid[pc.pos].entities if isinstance(e, entity.Character))
    if len(ents) == 0:
        print("No one here")
    elif len(ents) == 1:
        print("You attack {}!".format(ents[0]))
        pc.attack(ents[0])
    else:
        for e in ents:
            if v in e.name.upper():
                print("You attack {}!".format(e))
                pc.attack(e)
                return
        print("Who?")

commands = {
    'GO': go,
    'GET': get,
    'ATTACK': attack
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

@event.on("player.movement")
def main_ai(kwg):
    # do encounters
    ents = {e.uuid: True for e in m.grid[pc.pos].entities}
    event._log(event.Event("player.encounter", ents))


main()
