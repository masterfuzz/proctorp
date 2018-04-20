import event
import entity
import logging
L = logging.getLogger('quest')

class Quest(entity.LeveledEntity):
    def __init__(self, name, level=1):
        super(Quest,self).__init__(name, level)
        self.track = {}
        self.completed = {}

    def complete(self, name):
        self.completed[name] = True
        if all(v for v in self.completed.values()):
            event.log("quest.completed", sub= self.uuid)

    def require_kill(self, tag, n=1):
        track_name = "kill {} {}".format(n, tag)
        self.track[track_name] = 0
        self.completed[track_name] = False
        def req_hook(k):
            L.debug("Quest({}).req_hook[{}] called with {}".format(self.name, tag, k)) 
            if tag.upper() in entity.tags(k['sub']):
                L.debug("track updated")
                self.track[track_name] = self.track.get(track_name,0) + 1
                if self.track[track_name] >= n:
                    self.complete(track_name)
                else:
                    event.log("quest.updated", sub=self.uuid, req=tag, kind="kill", val=self.track[track_name], need=n)
        event.when("character.death", {'last_hit': entity.player_uuid})(req_hook)
        return self


