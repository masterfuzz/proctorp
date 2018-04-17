import event
import entity

class Quest(entity.LeveledEntity):
    def __init__(self, name, level=1):
        super(Quest,self).__init__(name, level)
        self.track = {}
        self.completed = {}

    def complete(name):
        self.completed[name] = True
        if all(v for v in self.completed.values()):
            event.log("quest.completed", {'sub': self.uuid})

    def require_kill(self, tag, n=1):
        track_name = "kill {} {}".format(n, tag)
        self.track[track_name] = 0
        self.completed[track_name] = False
        def req_hook(k):
            if tag in entity.tags(k['sub']):
                self.track[track_name] = self.track.get(track_name,0) + 1
                if self.track[track_name] >= n:
                    self.complete(track_name)
        event.when("character.death", {'last_hit': entity.player_uuid})(req_hook)
        return self
            


