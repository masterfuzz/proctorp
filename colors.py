import sys

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'



def error(text, stderr=False):
    cprint(text, FAIL, stderr)

def warn(text, stderr=False):
    cprint(text, WARNING, stderr)

def cprint(text, color=None, stderr=False):
   # if type(color) == str:
    #    color = getattr(colors, color)
    if not color:
        color = ''

    if stderr:
        sys.stderr.write(colored(text, color))
    else:
        sys.stdout.write(colored(text, color))

def colored(text, color=None):
    if not color:
        return text
    else:
        return "{}{}{}".format(color, text, ENDC)

def format_table(table, sep=' ', prefmt=None, postfmt=None):
    ident = (lambda x: x)
    if prefmt is None:
        prefmt = ident
    if postfmt is None:
        postfmt = ident

    cols = 1
    widths = {}
    for row in table:
        cols = max(cols, len(row))
        for col in range(len(row)):
            widths[col] = max(widths.get(col, 0), len(str(row[col])))

    table = map(prefmt, table)
    o = sep.join(['{{:<{}}}'.format(widths[c]) for c in range(cols)])

    return "\n".join(postfmt(o.format(*padright(row, cols))) for row in table)

def padright(l, n, pad=''):
    if len(l) < n:
        l += [pad] * n - len(l)
    else:
        return l

