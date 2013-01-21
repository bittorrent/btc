import argparse
import time
import hashlib
import os
from . import btclient
from . import utils
from .bencode import bdecode, bencode
from .btc import encoder, decoder, client, error

_description = 'add torrent to client'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('value')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-u', '--url', default=False, action='store_true')
    group.add_argument('-f', '--file', default=False, action='store_true')
    args = parser.parse_args()

    if not args.url and not args.file:
        args.file = os.path.exists(args.value)
        args.url = not args.file

    if args.url:
        args.value = utils.httpize(args.value)
        try:
            torrent = utils.get(args.value)
        except:
            error('invalid url: %s' % args.value)
        client.add_torrent_url(args.value)
    elif args.file:
        if not os.path.exists(args.value):
            error('no such file: %s' % args.value)
        try:
            f = open(args.value, 'rb')
            torrent = f.read()
            f.close()
        except:
            error('reading file: %s' % args.value)
        client.add_torrent_file(args.value)

    added = None

    try:
        decoded = bdecode(torrent)
        encoded = bencode(decoded['info'])
    except:
        error('invalid torrent file')

    h = hashlib.sha1(encoded).hexdigest().upper()
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
