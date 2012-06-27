#! /usr/bin/env python

import argparse
import sys
from btc import encoder, decoder, error, list_to_dict, dict_to_list, client

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--drop-data', default=False, action="store_true")
    parser.add_argument('-k', '--keep-torrent', default=False, action="store_true")
    args = parser.parse_args()

    if sys.stdin.isatty():
        error('no input')
    torrents = sys.stdin.read()

    try:
        torrents = decoder.decode(torrents)
    except ValueError:
        error('unexpected input: %s' % torrents)

    hashes = [t['hash'] for t in torrents]
    for h in hashes:
        client.remove_torrent(h, keep_data=not args.drop_data,
                              keep_torrent=args.keep_torrent)

    # FIXME: wait for torrents to be removed, only if
    # not args.keep_torrent ?!

    if not sys.stdout.isatty():
        d = list_to_dict(client.list_torrents(), 'hash')
        d = dict((h, d[h]) for h in hashes if h in d)
        print encoder.encode(dict_to_list(d, 'hash'))

if __name__ == '__main__':
    main()
