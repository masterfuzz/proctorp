import cellmap
import entity
import event


class Player(entity.Character):
    def __init__(self):
        self.pos = (0,0,0)
        super(Player, self).__init__(name="Player", level=1)

    @event.trigger("player.movement")
    def go_dir(self, n):
        self.pos = cellmap.add3d(self.pos, n)
        return {'new_pos': self.pos}

