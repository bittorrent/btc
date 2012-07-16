#! /usr/bin/env python

import argparse
import fnmatch
import sys
import re
from btc import encoder, decoder, error

_description = 'filter elements of a list'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nth', type=int, default=None)
    parser.add_argument('-f', '--firsts', type=int, default=None)
    parser.add_argument('-k', '--key', default='name')
    parser.add_argument('-s', '--case-sensitive', default=False, action="store_true")
    parser.add_argument('name', nargs='?', default=None)

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-e', '--equals', default=None)
    group.add_argument('-g', '--greater', default=None)
    group.add_argument('-l', '--less', default=None)

    group.add_argument('-T', '--true', dest='bool', default=None, action='store_true')
    group.add_argument('-F', '--false', dest='bool', default=None, action='store_false')

    args = parser.parse_args()

    if args.name and (args.equals or args.greater or args.less or args.bool):
        parser.error('cannot specify name and number or boolean options')

    if sys.stdin.isatty():
        error('no input')
    l = sys.stdin.read()

    try:
        l = decoder.decode(l)
    except ValueError:
        error('unexpected input: %s' % l)

    new = list()
    for o in l:
        if args.name is not None:
            def case(x):
                if args.case_sensitive:
                    return x
                return x.lower()
            if fnmatch.fnmatch(case(o[args.key]), case(args.name)):
                new.append(o)
        elif args.equals is not None:
            if float(o[args.key]) == float(args.equals):
                new.append(o)
        elif args.greater is not None:
            if float(o[args.key]) > float(args.greater):
                new.append(o)
        elif args.less is not None:
            if float(o[args.key]) < float(args.less):
                new.append(o)
        elif args.bool is not None:
            if bool(o[args.key]) is args.bool:
                new.append(o)
        else:
            new.append(o)

    if args.firsts is not None:
        new = new[0:min(args.firsts,len(new))]

    if args.nth is not None:
        new = [new[args.nth - 1]]

    print encoder.encode(new)

if __name__ == '__main__':
    main()
