import cellmap
import entity
import event


class Player(entity.Character):
    def __init__(self):
        super(Player, self).__init__(name="Player", level=1)
        self.pos = (0,0,0)

    @event.trigger("player.movement")
    def go_dir(self, n):
        self.pos = cellmap.add3d(self.pos, n)
        return {'new_pos': self.pos}

