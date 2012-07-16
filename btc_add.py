#! /usr/bin/env python

import argparse
import btclient
import time
from bencode import bencode, bdecode
import utils
import hashlib
from btc import encoder, decoder, client

_description = 'add torrent to client'

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', default=None)
    group.add_argument('-f', '--file', default=None)
    args = parser.parse_args()

    if args.url is not None:
        client.add_torrent_url(args.url)
        torrent = utils.get(args.url)
    else:
        client.add_torrent_file(args.file)
        f = open(args.file, 'rb')
        torrent = f.read()
        f.close()

    added = None
    h = hashlib.sha1(bencode(bdecode(torrent)['info'])).hexdigest().lower()
    while not added:
        l = client.list_torrents()
        for t in l:
            if t['hash'] == h:
                added = t
                break
        time.sleep(1)

    print(encoder.encode([added]))

if __name__ == '__main__':
    main()
