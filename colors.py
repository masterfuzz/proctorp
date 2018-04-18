import sys

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


write = sys.stdout.write

def cprint(text, color=None):
   # if type(color) == str:
    #    color = getattr(colors, color)
    write(colored(text, color))

def colored(text, color=None):
    if not color:
        return text
    else:
        return "{}{}{}".format(color, text, ENDC)

