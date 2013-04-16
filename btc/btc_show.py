import argparse
import fnmatch
import sys
import os
import re
from .btc import encoder, decoder, error, ordered_dict

_description = 'show values and items'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('keys', metavar='KEY', nargs='*', default=None,
                        help='keys associated with values to be printed')
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

    if not isinstance(l, list):
        error('input must be a list')
    elif args.keys and not all(isinstance(x, dict) for x in l):
        error('list items must be dictionaries when specifying a key')

    for i, e in enumerate(l):
        if isinstance(e, dict):
            keys = args.keys or ordered_dict(e).keys()
            if i != 0 and len(keys) > 1:
                print('')
            for key in keys:
                s = ''
                if len(keys) > 1:
                    s += '{}: '.format(key)
                try:
                    print('{}{}'.format(s, e[key]))
                except KeyError:
                    error('key not found: {}'.format(key))
        else:
            print(e)

if __name__ == '__main__':
    main()
