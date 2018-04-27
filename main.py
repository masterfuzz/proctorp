import signal
import cellmap
import player
import entity
import event
import socket
import logging as log
#sh = logging.FileHandler("debug.log")
log.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
                    level=log.INFO
#                    filename="debug.log",
                   )
log.info("Started logger")

HOST = ''
PORT = 5007

class GameServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.clients = []
        self.map = None
        log.info("Server initialized")

    def load(self):
        self.load_map()
        event.start()
        self.register_events()

    def register_events(self):
        log.debug("Registering server events")
        event.on("character.inventory.pickup")(self.pickup)
        event.on("player.action")(self.main_ai)
        event.on("character.inventory.drop")(self.dropped_item)
        event.on("login.request")(self.login_request)
        event.on("player.quit")(self.player_quit)
        log.info("Events registered")

    def player_quit(self, k):
        pass

    def login_request(self, k):
        para = k['client']
        user = k['user']
        new_pc = player.Player(name=user)
        new_pc.cell = self.map.grid[(0,0,0)]
        log.info("Login granted to {}".format(user))
        event.log("login.granted", para=para, pc=new_pc.uuid)

    def load_map(self):
        log.info("Loading map...\n")
        self.map = cellmap.Map()
        self.map.gen(10)
        log.info("Map loaded\n")

    def listen(self):
        self.sock.listen(5)
        log.info("Started listening")
        while True:
            client, addr = self.sock.accept()
            client.settimeout(60)
            #threading.Thread(target = self.listenToClient,args = (client,address)).start()
            log.info("Client connected")
            c = player.PlayerClient(client, addr)
            self.clients.append(c)
            c.start()

    def pickup(self, k):
        item = entity.ents[k['item']]
        self.map.grid[k['pos']].remove(item)
        entity.ents[k['sub']].get(item)

    def main_ai(self,kwg):
        # do encounters
        pc = entity.entities[kwg['sub']]
        ents = {e.uuid: True for e in self.map.grid[pc.pos].entities}
        ents['sub'] = pc.uuid
        event._log(event.Event("player.encounter", ents))

    def dropped_item(self,kwg):
        self.map.grid[kwg['pos']].entities.append(kwg['item'])


signal.signal(signal.SIGINT, lambda x,y: event.log(".", kill=event.KILL))
g = GameServer(HOST, PORT)
g.load()
g.listen()

