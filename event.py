import logging
L = logging.getLogger('events')
L.addHandler(logging.NullHandler())

class Event(object):
    def __init__(self, path=None, kwargs=None):
        if path is None:
            self.path = []
        else:
            self.path = path.split('.')
        if kwargs is None:
            self.args = {}
        else:
            self.args = kwargs
        self.args['_path'] = self.path

    def __repr__(self):
        return "{}(<{}>)".format(".".join(self.path), len(self.args))

class Hook:
    def __init__(self, path=None):
        self.methods = []
        if path is None:
            self.full_path = ""
        else:
            self.full_path = path
        self.children = {}

    def subscribe(self, path, method):
        if path:
            if not path[0]:
                self.subscribe(path[1:], method)
                return
            if path[0] not in self.children:
                new_hook = Hook(self.full_path + "." + path[0])
                self.children[path[0]] = new_hook
                L.debug("hooks: new path {}".format(new_hook.full_path))
            self.children[path[0]].subscribe(path[1:], method)
        else:
            L.debug("hooks: method subscribed at {}".format(self.full_path))
            self.methods.append(method)

    def invoke(self, e):
        return self._invoke(e.path, e)

    def __repr__(self):
        if self.full_path:
            return "{}:<{}>".format(self.full_path, len(self.children))
        else:
            return "{}:<{}>".format('.', len(self.children))

    def _invoke(self, path, e):
        for m in self.methods:
            L.debug("event: called at {}".format(self))
            args = e.args.copy()
            args['_ipath'] = self.full_path
            m(args)
        if path:
            if path[0] in self.children:
                self.children[path[0]]._invoke(path[1:], e)

root_hook = Hook()

def subscribe(path, method):
    root_hook.subscribe(path.split('.'), method)

def call_when(path, method, when):
    when(path, when)(method)


def _log(e):
    if e.args.get('_block'):
        return
    L.debug("event: {}".format(e))
    root_hook.invoke(e)

def log(path, **kwargs):
    _log(Event(path, kwargs))

#def test(msg):
#    print(msg)
#
#subscribe("hello.world", test)
#subscribe("hello", test)
#subscribe("", test)
#_log(Event("hello.world", {'some': 'message'}))
#_log(Event("hello", {'some': 'other message'}))
#_log(Event("", {'root', 'event'}))


class trigger:
    def __init__(self, path):
        self.path = path
    def __call__(self, f):
        def wrap(*args, **kwargs):
            res = f(*args, **kwargs)
            _log(Event(self.path, res))
            return res
        return wrap

class on:
    def __init__(self, path):
        self.path = path
    def __call__(self, f):
        subscribe(self.path, f)
        return f

class when:
    def __init__(self, path, query):
        self.path = path
        self.query = query

    def __call__(self, f):
        def check(kwargs):
            if all(self.query[k] == kwargs.get(k) for k in self.query):
                return f(kwargs)
            else:
                #L.debug("check missed {} != {}".format(self.query, kwargs))
                return None
        subscribe(self.path, check)
        return f

@on("")
def dbg_event(k):
    L.debug("{}".format(k))
