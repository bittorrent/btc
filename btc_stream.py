#! /usr/bin/env python

import subprocess
import argparse
import sys
import re
import os
from btc import encoder, decoder, error, warning, list_to_dict, dict_to_list, client

_description = 'stream torrent file locally'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', default='echo')
    parser.add_argument('-t', '--together', default=False, action='store_true')
    args = parser.parse_args()
    args.command = re.sub(r'[ \t]+', ' ', args.command)

    if sys.stdin.isatty():
        error('no input')
    files = sys.stdin.read()

    if len(files.strip()) == 0:
        exit(0)

    try:
        files = decoder.decode(files)
    except ValueError:
        error('unexpected input: %s' % files)

    if args.together:
        call = args.command.split(' ')
        for f in files:
            if 'fileid' not in f:
                warning('ignoring non-file entry: %s' % f['name'])
                continue
            call.append(client.torrent_stream_url(f['sid'], f['fileid']))
        if sys.stdout.isatty():
            print 'running: %s' % ' '.join(call)
        subprocess.call(call)
    else:
        for f in files:
            if 'fileid' not in f:
                warning('ignoring non-file entry: %s' % f['name'])
                continue
            call = args.command.split(' ')
            url = client.torrent_stream_url(f['sid'], f['fileid'])
            call.append(url)
            if sys.stdout.isatty():
                print 'running: %s' % ' '.join(call)
            subprocess.call(call)

if __name__ == '__main__':
    main()
