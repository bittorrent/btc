import argparse
import fnmatch
import sys
import os
import re
import collections
from .btc import encoder, decoder, error, ordered_dict

_description = 'show values and items'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('key', metavar='KEY', nargs='?', default=None,
                        help='key associated with values to reduce')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--min', action='store_true', default=None)
    group.add_argument('--max', action='store_true', default=None)
    group.add_argument('--sum', action='store_true', default=None)
    group.add_argument('--mean', action='store_true', default=None)
    group.add_argument('--dist', action='store_true', default=None)
    group.add_argument('--count', action='store_true', default=None)
    group.add_argument('--unique', action='store_true', default=None)
    group.add_argument('--join', metavar='STR', default=None, help='string to use for a join')
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
    elif args.key and not all(isinstance(x, dict) for x in l):
        error('list items must be dictionaries when specifying a key')

    out = []
    for i, e in enumerate(l):
        try:
            out.append(e[args.key] if args.key else e)
        except KeyError:
            error('key not found: {}'.format(args.key))

    f = None
    if args.min:
        f = min
    elif args.max:
        f = max
    elif args.sum:
        if not all(isinstance(x, float) or isinstance(x, int) for x in out):
            error('sum requires numerical values')
        f = sum
    elif args.mean:
        if not all(isinstance(x, float) or isinstance(x, int) for x in out):
            error('mean requires numerical values')
        f = lambda l: float(sum(l)) / len(l) if len(l) > 0 else float('nan')
    elif args.dist:
        f = lambda l: dict(collections.Counter(l).most_common())
    elif args.count:
        f = lambda l: len(l)
    elif args.unique:
        f = lambda l: list(set(l))
    elif args.join is not None:
        f = lambda l: args.join.join(l)
    else:
        f = lambda l: '\n'.join(l)

    if args.unique or args.dist:
        print(encoder.encode(f(out)))
    else:
        print(f(out))

if __name__ == '__main__':
    main()
