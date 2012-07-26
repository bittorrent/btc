#! /usr/bin/env python

import argparse
import sys
from btc import encoder, decoder, error, list_to_dict, dict_to_list

_description = 'sort elements of a list'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', default='name')
    parser.add_argument('-s', '--case-sensitive', default=False, action='store_true')
    parser.add_argument('-r', '--reverse', default=False, action='store_true')
    args = parser.parse_args()

    if sys.stdin.isatty():
        error('no input')
    l = sys.stdin.read()

    if len(l.strip()) == 0:
        exit(0)

    try:
        l = decoder.decode(l)
    except ValueError:
        error('unexpected input: %s' % l)

    def key(x):
        if (isinstance(x[args.key], str) or isinstance(x[args.key], unicode)) \
               and not args.case_sensitive:
            return x[args.key].lower()
        return x[args.key]

    l = sorted(l, key=key)

    if args.reverse:
        l = list(reversed(l))

    print encoder.encode(l)

if __name__ == '__main__':
    main()
