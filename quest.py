import event
import entity
import logging
L = logging.getLogger('quest')

class Quest(entity.LeveledEntity):
    def __init__(self, name, level=1):
        super(Quest,self).__init__(name, level)
        self.track = {}
        self.completed = {}
        self.accepted = False
        self.acceptees = []

    def accept(self, by=None):
        if by in self.acceptees:
            return
        self.acceptees.append(by)
        self.accepted = True
        event.log("quest.accepted", sub=by, obj=self.uuid)

    def complete(self, name, by=None):
        self.completed[name] = True
        if all(v for v in self.completed.values()):
            event.log("quest.completed", sub=by, obj=self.uuid)

    def require_kill(self, tag, n=1):
        track_name = "kill {} {}".format(n, tag)
        self.track[track_name] = 0
        self.completed[track_name] = False
        def req_hook(k):
            print("REQ HOOK WAS CALLED")
            if k.get('last_hit') not in self.acceptees:
                return
            L.debug("Quest({}).req_hook[{}] called with {}".format(self.name, tag, k)) 
            if tag.upper() in entity.tags(k['sub']):
                L.debug("track updated")
                self.track[track_name] = self.track.get(track_name,0) + 1
                if self.track[track_name] >= n:
                    self.complete(track_name, by=k.get('last_hit'))
                else:
                    event.log("quest.updated", sub=self.uuid, req=tag, kind="kill", val=self.track[track_name], need=n)
        event.on("character.death")(req_hook)
        print("I TRIED TO REGISTER MY EVENT!")
        return self


