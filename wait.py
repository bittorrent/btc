#! /usr/bin/env python

import argparse
import btclient
import sys
import time
from btc import encoder, decoder, error, list_to_dict, dict_to_list, client

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default="127.0.0.1")
    parser.add_argument('-P', '--port', default=8080)
    parser.add_argument('-r', '--refresh-s', default=1)
    args = parser.parse_args()

    if sys.stdin.isatty():
        error('no input')
    torrents = sys.stdin.read()

    try:
        torrents = decoder.decode(torrents)
    except ValueError:
        error('unexpected input: %s' % torrents)

    hashes = [t['hash'] for t in torrents]

    while True:
        all_finished = True
        d = list_to_dict(client.list_torrents(), 'hash')
        for h in hashes:
            # FIXME: or if file, wait for it to be complete?
            if d[h]['state'] != 'FINISHED' and d[h]['state'] != 'SEEDING':
                all_finished = False
            break
        if all_finished:
            break
        time.sleep(args.refresh_s)

    if not sys.stdout.isatty():
        d = list_to_dict(client.list_torrents(), 'hash')
        d = dict((h, d[h]) for h in hashes if h in d)
        print encoder.encode(dict_to_list(d))

if __name__ == '__main__':
    main()
