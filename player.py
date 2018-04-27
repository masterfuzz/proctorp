from __future__ import print_function
import colors
import cellmap
import entity
import event
import uuid
import threading
import logging
L = logging.getLogger('client')


class Player(entity.Character):
    def __init__(self, name=None, level=1):
        if name is None:
            name = "Player"
        super(Player, self).__init__(name, level)
        L.debug("new player init")

    @event.trigger("player.action.movement")
    def go_dir(self, n):
        self.pos = cellmap.add3d(self.pos, n)
        return {'new_pos': self.pos, 'sub': self.uuid}

    def target(self, name, cls=None, inv=None):
        if inv:
            loc = self.inv
        else:
            loc = self.cell.entities
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

class PlayerClient(threading.Thread):
    def __init__(self, sock, addr):
        super(PlayerClient,self).__init__()
        self.sock = sock
        self.addr = addr
        self.mode = self.login
        self.uuid = uuid.uuid1()
        self.pc = None
        self.welcome()
        self.commands = {
            'GO': self.go,
            'GET': self.get,
            'ATTACK': self.attack,
            'SELF': self.look_self,
            'LOOK': self.look,
            'EQUIP': self.equip,
            'DROP': self.drop,
            'UNEQUIP': self.unequip,
            'QUIT': self.quit,
            'HELP': self.cmdhelp
        }
        L.info("client init")

    def print(self, txt, color=None):
        #todo: check if socket is open
        self.sock.send(colors.colored(txt, color=color))

    def welcome(self):
        self.print("Login: ")

    def login(self, data):
        event.log("login.request", client=self.uuid, user=data)
        self.mode = self.wait_login
        self.print("Logging in please wait...\n")
        event.on("login.granted", para=self.uuid)(self.login_success)
        event.on("login.denied", para=self.uuid)(self.login_fail)

    def wait_login(self, data):
        self.sock.send("\n....\n")
        # ignore data

    def login_fail(self, k):
        self.print("Login failed! {}\n".format(k))
        self.sock.close()

    def login_success(self, k):
        self.pc = entity.entities[k['pc']]
        self.sock.send("Login success!\nRetrieved character {}\n".format(self.pc))
        self.mode = self.main_actions

    def main_actions(self, d):
        self.print(self.pc.cell.look()+"\n")
        #dirs = self.pc.cell.get_dirs()
        #names = map(lambda x: cellmap.dir_name(*x), dirs)
        #self.print(", ".join(names)+"\n\n> ", color=colors.OKGREEN)
        v = d.upper().split(' ', 1)
        if v[0] in self.commands:
            if len(v) > 1:
                self.commands[v[0]](v[1:][0])
            else:
                self.commands[v[0]](None)
        else:
            self.print("I don't understand that command.\nYou said: '{}'\n".format(v))

    #######
    ## Commands
    #######
    def cmdhelp(self,v):
        msg = "Possible commands are:\n"
        msg += "\n".join(self.commands.keys())
        msg += "\n"
        self.print(msg, color=colors.WARNING)

    def go(self,v):
        dirs = self.pc.cell.get_dirs()
        choice = cellmap.d2n(v)
        if choice in dirs:
            self.pc.go_dir(choice)
        else:
            self.print("can't go that way ({})\n".format(choice))

    def get(self,v):
        t = self.pc.target(v, cls=entity.Item)
        if t:
            self.pc.get(t)
            self.pc.cell.remove(t)
            self.print("You pick up {}\n".format(t))
            event.log("player.action.get", sub=self.pc.uuid)
        else:
            if v:
                self.print("I don't see {} here\n".format(v))
            else:
                self.print("There's nothing to get\n")

    def attack(self,v):
        t = self.pc.target(v, cls=entity.Character)
        if t:
            self.pc.attack(t)
            event.log("player.action.attack", sub=self.pc.uuid)
        else:
            self.print("I don't see '{}' here.\n".format(v))

    def equip(self, v):
        t = self.pc.target(v, cls=entity.Weapon, inv=True)
        if t:
            self.pc.equip(t)
            event.log("player.action.equip", sub=self.pc.uuid)
        else:
            self.print("Equip what?\n")

    def unequip(self, v):
        if self.pc.weapon:
            self.pc.unequip()
            event.log("player.action.unequip", sub=self.pc.uuid)
        else:
            self.print("You're not holding a weapon\n")

    def drop(self, v):
        if self.pc.weapon and self.pc.weapon.name.upper() == v:
            self.pc.unequip()
        t = self.pc.target(v, inv=True)
        if t:
            self.pc.drop(t)
            event.log("player.action.drop", sub=self.pc.uuid)
        else:
            self.print("Drop what?\n")

    def look_self(self, v):
        self.print(self.pc.look()+"\n", color=colors.OKBLUE)

    def look(self, v):
        t = self.pc.target(v)
        if t:
            self.print(t.look()+"\n")
        else:
            self.print("At what?\n")

    def quit(self, v):
        L.info("client disconnect")
        self.print("Bye!\n\n")
        event.log("player.quit", client=self.uuid, pc=self.pc.uuid)
        self.sock.close()

    def run(self):
        L.debug("main loop start")
        size = 1024
        while True:
            L.debug("loop top")
            try:
                data = self.sock.recv(size).strip()
                if data:
                    self.mode(data)
                else:
                    raise Exception('self.sock disconnected')
            except Exception as e:
                self.sock.close()
                L.info("client disconnect")
                L.error(str(e))
                return False

