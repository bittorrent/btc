import argparse
import sys
import fnmatch
import os
from btc import encoder, decoder, error, warning, client, ordered_dict, config

_description = 'list files of torrents'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', nargs='?', default=None)
    parser.add_argument('-s', '--case-sensitive', default=False, action="store_true")
    parser.add_argument('-w', '--windows', default=False, action='store_true',
                        help='bittorrent client is running on windows')
    args = parser.parse_args()

    if not args.windows and 'windows' in config:
        args.windows = config['windows']

    if sys.stdin.isatty():
        error('no input torrents')
    torrents = sys.stdin.read()

    if len(torrents.strip()) == 0:
        exit(0)

    try:
        torrents = decoder.decode(torrents)
    except ValueError:
        error('unexpected input: %s' % torrents)

    sids = {}
    hashes = []
    for t in torrents:
        if 'hash' not in t or 'sid' not in t or 'fileid' in t:
            warning('ignoring non-torrent entry')
            continue
        sids[t['hash']] = t['sid']
        hashes.append(t['hash'])

    if len(hashes) == 0:
        print encoder.encode([])
        exit(0)

    files = client.torrent_files(hashes, sids)
    matched = []
    if args.name:
        for f in files:
            def case(x):
                if args.case_sensitive:
                    return x
                return x.lower()

            if fnmatch.fnmatch(case(f['name']), case(args.name)):
                matched.append(f)
    else:
        matched = files

    for f in matched:
        if args.windows and os.sep == '/':
            f['name'] = f['name'].replace('\\', '/')
        elif not args.windows and os.sep == '\\':
            f['name'] = f['name'].replace('/', '\\')

    matched = sorted(matched, key=lambda x: x['name'].lower())
    print encoder.encode([ordered_dict(d) for d in matched])

if __name__ == '__main__':
    main()
