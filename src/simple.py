from __future__ import with_statement
import sys
from lib import parser
from lib import builtin
from lib.exception import Exception_base

def print_string(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def read_string():
    return sys.stdin.readline()[:-1]

def run_file(src):
    try:
        with open(sys.argv[1], 'r') as p:
            src = p.read()
    except IOError:
        print_string('[Error-IO] That file doesn\'t exist!\n')
        sys.exit(1)
    
    try:
        parser.parse(src).evaluate()
    except Exception_base as e:
        print_string('[%s] %s\n' % (e.name, str(e)))
    except KeyboardInterrupt:
        print_string('\nAborted by user.\n')

def run_repl():
    print_string('SimpleLang REPL (platform : %s)\n' % sys.platform)

    while 1:
        try:
            print_string('> ')
            src = read_string()

            builtin.called_main = False
            parser.parse(src).evaluate()

            if builtin.called_print:
                print_string('\n')
                builtin.called_print = False
        except Exception_base as e:
            print_string('[%s] %s\n' % (e.name, str(e)))
        except KeyboardInterrupt:
            print_string('\nAborted by user.\n')
            break

if __name__ == '__main__':
    args = sys.argv[1:]

    if args:
        run_file(args[0])
    else:
        run_repl()
