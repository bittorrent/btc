#! /usr/bin/env python

import argparse
import btclient
from btc import encoder, decoder, client

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', default=None)
    group.add_argument('-f', '--file', default=None)
    args = parser.parse_args()

    if args.url is not None:
        client.add_torrent_url(args.url)
    else:
        client.add_torrent_file(args.file)

    # FIXME: wait for torrent to be added

    # FIXME: print torrent info

if __name__ == '__main__':
    main()
