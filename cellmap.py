import random
import entities

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
                print("new cell @{}".format(c))
                new_cell = Cell.rand()
                new_cell.pos = c
                self.grid[c] = new_cell
                self.cells.append(new_cell)
            else:
                print('no free space at {}'.format(c))
                c = random.choice(self.cells).pos
        for c in self.cells:
            for n in self.get_dirs(*c.pos):
                c.neighbor[n] = self.get_neighbor(*(c.pos+n))

        for e in entities.entities:
            c = random.choice(self.cells)
            print("{} placed at {}".format(e, c.pos))
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
        d += 'WEST'
    if x == 1:
        d += 'EAST'
    if z == -1:
        d += ' (DOWN)'
    if z == 1:
        d += ' (UP)'
    return d

class Cell:
    def __init__(self):
        self.neighbor = {}
        self.entities = []
        self.pos = (0,0,0)
        self.terrain = None
        self.desc = ""

    def __str__(self):
        return '#'

    @staticmethod
    def rand():
        c = Cell()
        c.terrain = random.choice(("Grassland", "Mountains", "Forest", "River"))
        return c

    def populate(self, *e):
        self.entities += e

    def look(self):
        desc = self.desc
        desc += "\nTerrain: {}\n".format(self.terrain)
        if self.entities:
            desc += " and ".join(map(str, self.entities))
            desc += " is here"
        return desc

class SparseArray:
    def __init__(self, default=None):
        self._store = {}
        self.default = default

    def __getitem__(self, key):
        if type(key) != int:
            raise TypeError("Should be int")
        return self._store.get(key, self.default)

    def __setitem__(self, key, value):
        if type(key) != int:
            raise TypeError("Should be int")
        self._store[key] = value

    def to_list(self, min_index=None, max_index=None):
        if min_index is None:
            min_index = min(self._store.keys())
        if max_index is None:
            max_index = max(self._store.keys())
        return [self._store.get(x, self.default) for x in range(min_index, max_index)]

    def __contains__(self, key):
        return key in self._store


class SparseArray2D:
    def __init__(self, default=None):
        self._store = {}
        self.default = default

    def __contains__(self, key):
        x, y = key
        return x in self._store and y in self._store[y]

    def __getitem__(self, key):
        if type(key) == int:
            if key in self._store:
                return self._store[key]
            else:
                self._store[key] = SparseArray(self.default)
                return self._store[key]

        x, y = key
        if x in self._store:
            return self._store[x][y]
        else:
            return self.default

    def __setitem__(self, key, value):
        x, y = key
        if x not in self._store:
            self._store[x] = SparseArray(self.default)
        self._store[x][y] = value

class SparseArray3D:
    def __init__(self, default=None):
        self._store = {}
        self.default = default

    def __contains__(self, key):
        x, y, z = key
        return x in self._store and y in self._store[x] and z in self._store[x][y]

    def __getitem__(self, key):
        if type(key) == int:
            if key in self._store:
                return self._store[key]
            else:
                self._store[key] = SparseArray2D(self.default)
                return self._store[key]

        if len(key) == 2:
            x, y = key
            if x not in self._store:
                self._store[x] = SparseArray2D(self.default)
            return self._store[x][y]

        x, y, z = key
        if x in self._store:
            return self._store[x][y][z]
        else:
            return self.default

    def __setitem__(self, key, value):
        x, y, z = key
        if x not in self._store:
            self._store[x] = SparseArray2D(self.default)
        self._store[x][y][z] = value


grid = SparseArray3D(0)
m = Map()
