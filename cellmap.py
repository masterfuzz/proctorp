import random
import entities
import logging
L = logging.getLogger('map')
L.addHandler(logging.NullHandler())

class Map:
    def __init__(self):
        self.grid = {}
        self.cells = []

    def gen(self, n=100):
        c = (0,0,0)
        self.grid[c] = Cell.rand()
        for i in range(n):
            fs = self.free_space(*c)
            if fs:
                c = rand_neighbor(*c, opts=fs)
                L.debug("new cell @{}".format(c))
                new_cell = Cell.rand()
                new_cell.pos = c
                self.grid[c] = new_cell
                self.cells.append(new_cell)
            else:
                L.debug('no free space at {}'.format(c))
                c = random.choice(self.cells).pos
        for c in self.cells:
            for n in self.get_dirs(*c.pos):
                c.neighbor[n] = self.get_neighbor(*(c.pos+n))

        for e in entities.entities:
            c = random.choice(self.cells)
            L.debug("{} placed at {}".format(e, c.pos))
            c.populate(e)

    def has_neighbor(self, px,py,pz, nx,ny,nz):
        return (nx+px,ny+py,nz+pz) in self.grid

    def get_neighbor(self, px,py,pz, nx,ny,nz):
        return self.grid.get((px+nx,py+ny,pz+nz), None)

    def free_space(self, px,py,pz):
        return [n for n in neighbors if not self.has_neighbor(px,py,pz,*n)]

    def get_dirs(self, px,py,pz):
        return (n for n in neighbors if self.has_neighbor(px,py,pz,*n))

    def _show(self, x,y,z):
        if (x,y,z) in self.grid:
            return str(self.grid[x,y,z])
        else:
            return '.'

    def show2d(self, x,y,z, n=2):
        o = ''
        for i in range(x-n,x+n):
            for j in range(y-n,y+n):
                o += self._show(i,j,z)
            o += '\n'
        return o


neighbors=((0,0,1),(0,0,-1),(0,1,0),
           (0,1,1),(0,1,-1),(0,-1,0),(0,-1,1),
           (0,-1,-1),(1,0,0),(1,0,1),(1,0,-1),
           (1,1,0),(1,1,1),(1,1,-1),(1,-1,0),
           (1,-1,1),(1,-1,-1),(-1,0,0),(-1,0,1),
           (-1,0,-1),(-1,1,0),(-1,1,1),(-1,1,-1),
           (-1,-1,0),(-1,-1,1),(-1,-1,-1))
neighbors=list(x for x in neighbors if x[2] == 0)
dirs={
    'NORTH': (0,1,0),
    'SOUTH': (0,-1,0),
    'EAST': (1,0,0),
    'WEST': (-1,0,0),
    'UP': (0,0,1),
    'DOWN': (0,0,-1)
}

def add3d(a,b):
    ax,ay,az = a
    bx,by,bz = b
    return (ax+bx,ay+by,az+bz)

def d2n(ds):
    #simple for now
    n = (0,0,0)
    for e in ds.upper().split():
        if e in dirs:
            n = add3d(n, dirs[e])
    return n


def rand_neighbor(x,y,z,opts=None):
    if opts:
        nx,ny,nz= random.choice(opts)
    else:
        nx,ny,nz= random.choice(neighbors)
    return nx+x,ny+y,nz+z

def dir_name(x,y,z):
    if x==y==z==0:
        return 'HERE'
    d = ''
    if y == -1:
        d += 'SOUTH'
    if y == 1:
        d += 'NORTH'
    if x == -1:
        d += ' WEST'
    if x == 1:
        d += ' EAST'
    if z == -1:
        d += ' DOWN'
    if z == 1:
        d += ' UP'
    return d.strip()

class Cell:
    def __init__(self):
        self.neighbor = {}
        self.entities = []
        self.pos = (0,0,0)
        self.terrain = None
        self.desc = ""

    def get_dirs(self):
        return self.neighbor.keys()

    def __str__(self):
        return '#'

    @staticmethod
    def rand():
        c = Cell()
        c.terrain = random.choice(("Grassland", "Mountains", "Forest", "River"))
        return c

    def remove(self, e):
        for i in range(len(self.entities)):
            if e.uuid == self.entities[i].uuid:
                del self.entities[i]
                return


    def populate(self, *e):
        for x in e:
            x.pos = self.pos
        self.entities += e

    def look(self):
        desc = self.desc
        desc += "\nTerrain: {}\n".format(self.terrain)
        if self.entities:
            desc += " and ".join(map(str, self.entities))
            desc += " is here"
        return desc

