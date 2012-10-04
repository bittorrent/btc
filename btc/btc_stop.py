import argparse
import sys
import time
from btc import encoder, decoder, error, list_to_dict, dict_to_list, client

_description = 'stop torrent'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delay', type=int, default=0)
    args = parser.parse_args()

    if sys.stdin.isatty():
        parser.error('no input, pipe another btc command output into this command')
    torrents = sys.stdin.read()

    if len(torrents.strip()) == 0:
        exit(0)

    try:
        torrents = decoder.decode(torrents)
    except ValueError:
        error('unexpected input: %s' % torrents)

    time.sleep(args.delay)

    hashes = [t['hash'] for t in torrents]
    for h in hashes:
        client.stop_torrent(h)

    while True:
        d = list_to_dict(client.list_torrents(), 'hash')
        all_stopped = True
        for h in d:
            if h not in hashes:
                continue
            if d[h]['state'] not in ('STOPPED', 'FINISHED'):
                all_stopped = False
                break
        if all_stopped:
            break
        time.sleep(1)

    if not sys.stdout.isatty():
        d = list_to_dict(client.list_torrents(), 'hash')
        d = dict((h, d[h]) for h in hashes if h in d)
        print encoder.encode(dict_to_list(l))

if __name__ == '__main__':
    main()
