import argparse
import sys
import time
from . import btclient
from .btc import encoder, decoder, error, list_to_dict, dict_to_list, client

_description = 'wait for torrents or files download to complete'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--refresh-s', default=1)
    args = parser.parse_args()

    if sys.stdin.isatty():
        torrents = sorted(client.list_torrents(), key=lambda x: x['name'].lower())
    else:
        torrents = sys.stdin.read()

        if len(torrents.strip()) == 0:
            exit(1)

        try:
            torrents = decoder.decode(torrents)
        except ValueError:
            error('unexpected input: %s' % torrents)

    hashes = [t['hash'] for t in torrents if 'fileid' not in t]
    fileids = [(t['fileid'], t['hash'], t['sid']) for t in torrents
               if 'fileid' in t]

    while True:
        if len(fileids) == 0 and len(hashes) == 0:
            break

        d = list_to_dict(client.list_torrents(), 'hash')

        all_finished = True

        for h in hashes:
            if d[h]['state'] not in ('FINISHED', 'SEEDING', 'QUEUED_SEED'):
                all_finished = False
                break

        files = client.torrent_files([f[1] for f in fileids],
                                     dict([(f[1], f[2]) for f in fileids]))

        files_hashes = set([f['hash'] for f in files])
        files_dict = dict([(h, dict()) for h in files_hashes])
        for f in files:
            files_dict[f['hash']][f['fileid']] = f

        for (fileid, h, sid) in fileids:
            f = files_dict[h][fileid]
            if float(f['downloaded']) < float(f['size']):
                all_finished = False
                break

        if all_finished:
            break
        time.sleep(args.refresh_s)

    if not sys.stdout.isatty():
        d = list_to_dict(client.list_torrents(), 'hash')
        d = dict((h, d[h]) for h in hashes if h in d)
        print(encoder.encode(dict_to_list(d)))

if __name__ == '__main__':
    main()
