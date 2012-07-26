#! /usr/bin/env python

import argparse
import sys
import os
from btc import encoder, decoder, error, warning, list_to_dict, dict_to_list, client, config

_description = 'download torrent file locally'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', default='.')
    parser.add_argument('-o', '--output', default=None)
    parser.add_argument('-w', '--windows', default=False, action='store_true',
                        help='bittorrent client is running on windows')
    args = parser.parse_args()

    if not args.windows and 'windows' in config:
        args.windows = config['windows']

    if sys.stdin.isatty():
        error('no input')
    files = sys.stdin.read()

    if len(files.strip()) == 0:
        exit(0)

    try:
        files = decoder.decode(files)
    except ValueError:
        error('unexpected input: %s' % files)

    if not os.path.exists(args.directory):
        error('no such directory: %s' % args.directory)

    if args.output and len(files) > 1:
        if sys.stdout.isatty():
            warning('multiple files: --output is ignored')

    for f in files:
        if 'fileid' not in f:
            warning('ignoring non-file entry: %s' % f['name'])
            continue

        if args.windows and os.sep == '/':
            f['name'] = f['name'].replace('\\', '/')
        elif not args.windows and os.sep == '\\':
            f['name'] = f['name'].replace('/', '\\')

        filename = args.output or f['name']

        complete = float(f['downloaded']) / float(f['size']) * 100
        if sys.stdout.isatty() and complete < 100.0:
            print 'skipping incomplete file: %s' % f['name']
            continue

        if args.output and len(files) > 1:
            filename = f['name']
        if args.output and len(files) == 1:
            directory = os.path.dirname(os.path.join(args.directory, args.output))
            if not os.path.exists(directory):
                error('no such directory: %s' % directory)
        else:
            directory = os.path.dirname(os.path.join(args.directory, f['name']))
            if not os.path.exists(directory):
                os.makedirs(directory)

        if sys.stdout.isatty():
            print 'downloading: %s' % os.path.join(args.directory, filename)

        client.torrent_download_file(f['sid'], f['fileid'], filename, args.directory)

    if not sys.stdout.isatty():
        l = client.list_torrents()
        print encoder.encode(l)

if __name__ == '__main__':
    main()
