import argparse
import fnmatch
import sys
import re
from .btc import encoder, decoder, error

_description = 'show values and items'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('key', metavar='KEY', nargs='?', default=None,
                        help='key associated with value to be printed')
    args = parser.parse_args()

    if sys.stdin.isatty():
        parser.error('no input, pipe another btc command output into this command')
    l = sys.stdin.read()

    if len(l.strip()) == 0:
        exit(1)

    try:
        l = decoder.decode(l)
    except ValueError:
        error('unexpected input: %s' % l)

    if isinstance(l, list):
        i = 0
        for e in l:
            if isinstance(e, dict):
                if args.key is not None:
                    try:
                        print(e[args.key])
                    except KeyError:
                        error('key not found: {}'.format(args.key))
                else:
                    if i != 0:
                        print()
                    items = list(e.items())
                    items = sorted(items, key=lambda x: x[0])
                    print('\n'.join(['{}: {}'.format(k, v) for k, v in items]))
            else:
                error('unexpected input: {}'.format(e))
            i += 1

if __name__ == '__main__':
    main()
