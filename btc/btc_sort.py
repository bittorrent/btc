import argparse
import sys
from .btc import encoder, decoder, error, list_to_dict, dict_to_list, ordered_dict

try:
    unicode
except NameError:
    unicode = str

_description = 'sort elements of a list'

# TODO: add support for dates (date_added, date_completed)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', default='name')
    parser.add_argument('-s', '--case-sensitive', default=False, action='store_true')
    parser.add_argument('-r', '--reverse', default=False, action='store_true')
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

    def key(x):
        key = x[args.key]
        if ((isinstance(x[args.key], str)
             or isinstance(x[args.key], unicode))
            and not args.case_sensitive):
            return key.lower()
        return key

    l = sorted(l, key=key)

    if args.reverse:
        l = list(reversed(l))

    print(encoder.encode([ordered_dict(d) for d in l]))

if __name__ == '__main__':
    main()
