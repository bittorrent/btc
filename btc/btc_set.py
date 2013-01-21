import argparse
import sys
import os
from .btc import encoder, decoder, error, config_file, original_config

_description = 'manage settings file'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('key')
    parser.add_argument('value', nargs='?', default=None)
    parser.add_argument('-f', '--force-quotes', default=False, action="store_true")
    parser.add_argument('-d', '--delete', default=False, action="store_true")
    args = parser.parse_args()

    config = original_config

    if args.delete:
        if args.value:
            error('value was given but delete was requested')

        if args.key not in config:
            error('not in settings file: %s' % args.key)
        del config[args.key]
    else:
        if args.value is None:
            error('value is missing')

        if not args.force_quotes:
            try:
                args.value = decoder.decode(args.value)
            except ValueError:
                pass

        config[args.key] = args.value

    f = open(config_file, 'w')
    f.write(encoder.encode(config))
    f.close()

if __name__ == '__main__':
    main()
