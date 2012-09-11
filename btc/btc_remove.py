import argparse
import sys
import time
from btc import encoder, decoder, error, list_to_dict, dict_to_list, client

_description = 'remove torrent'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--drop-data', default=False, action="store_true")
    parser.add_argument('-k', '--keep-torrent', default=False, action="store_true")
    args = parser.parse_args()

    if sys.stdin.isatty():
        error('no input torrents')
    torrents = sys.stdin.read()

    if len(torrents.strip()) == 0:
        exit(0)

    try:
        torrents = decoder.decode(torrents)
    except ValueError:
        error('unexpected input: %s' % torrents)

    hashes = [t['hash'] for t in torrents]
    for h in hashes:
        client.remove_torrent(h, keep_data=not args.drop_data,
                              keep_torrent=args.keep_torrent)

    while True:
        l = client.list_torrents()
        all_removed = True
        for t in l:
            if t['hash'] in hashes:
                all_removed = False
                break
        if all_removed:
            break
        time.sleep(1)

if __name__ == '__main__':
    main()
