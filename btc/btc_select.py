import argparse
import fnmatch
import sys
import os
import re
from .btc import encoder, decoder, error, ordered_dict

_description = 'select some values'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('keys', metavar='KEY', nargs='+', default=None,
                        help='keys associated with values to be selected')
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
    elif not all(isinstance(x, dict) for x in l):
        error('list items must be dictionaries')

    out = []
    for i, e in enumerate(l):
        e_out = {}
        for key in args.keys:
            try:
                if len(args.keys) == 1:
                    e_out = e[key]
                else:
                    e_out[key] = e[key]
            except KeyError:
                error('key not found: {}'.format(key))
        out.append(e_out)

    if len(args.keys) > 1:
        print(encoder.encode([ordered_dict(d) for d in out]))
    else:
        print(encoder.encode([e for e in out]))

if __name__ == '__main__':
    main()
