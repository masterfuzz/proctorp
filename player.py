from __future__ import print_function
import cellmap
import entity
import event


class Player(entity.Character):
    def __init__(self):
        super(Player, self).__init__(name="Player", level=1)

    @event.trigger("player.action.movement")
    def go_dir(self, n):
        self.pos = cellmap.add3d(self.pos, n)
        return {'new_pos': self.pos, 'sub': self.uuid}

