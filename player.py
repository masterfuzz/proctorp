from __future__ import print_function
import colors
import cellmap
import entity
import event
import uuid
import threading


class Player(entity.Character):
    def __init__(self):
        super(Player, self).__init__(name="Player", level=1)

    @event.trigger("player.action.movement")
    def go_dir(self, n):
        self.pos = cellmap.add3d(self.pos, n)
        return {'new_pos': self.pos, 'sub': self.uuid}

class PlayerClient(threading.Thread):
    def __init__(self, sock, addr):
        super(PlayerClient,self).__init__()
        self.sock = sock
        self.addr = addr
        self.mode = self.login
        self.uuid = uuid.UUID1()
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

    def print(self, txt, color=None):
        #todo: check if socket is open
        self.sock.send(colors.colored(txt, color=color))

    def welcome(self):
        self.print("Login: ")

    def login(self, data):
        event.log("login.request", para=self.uuid, user=data.trim())
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
        self.print(self.here.look()+"\n")
        #dirs = self.here.get_dirs()
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

        

    def run(self):
        size = 1024
        while True:
            try:
                data = self.sock.recv(size).strip()
                if data:
                    self.mode(data)
                else:
                    raise Exception('self.sock disconnected')
            except:
                self.sock.close()
                return False

