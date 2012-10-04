import subprocess
import argparse
import sys
import re
import os
from btc import encoder, decoder, error, warning, list_to_dict, dict_to_list, client

_description = 'stream torrent file locally'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', default=None)
    parser.add_argument('-t', '--together', default=False, action='store_true')
    args = parser.parse_args()

    if args.command:
        args.command = re.sub(r'[ \t]+', ' ', args.command)
    else:
        warning('no stream command specified, outputing streaming links')

    if sys.stdin.isatty():
        parser.error('no input')
    files = sys.stdin.read()

    if len(files.strip()) == 0:
        exit(0)

    try:
        files = decoder.decode(files)
    except ValueError:
        error('unexpected input: %s' % files)

    if args.together:
        call = []
        if args.command:
            call = args.command.split(' ')
        for f in files:
            if 'fileid' not in f:
                warning('ignoring non-file entry: %s' % f['name'])
                continue
            call.append(client.torrent_stream_url(f['sid'], f['fileid']))
        if sys.stdout.isatty() and args.command:
            print 'running: %s' % ' '.join(call)
            try:
                subprocess.call(call)
            except OSError as e:
                error(e.strerror)
        elif sys.stdout.isatty():
            for (ff, url) in zip([f['name'] for f in files if 'fileid' in f], call):
                print '%s' % url,
            print
    else:
        for f in files:
            if 'fileid' not in f:
                warning('ignoring non-file entry: %s' % f['name'])
                continue
            call = []
            if args.command:
                call = args.command.split(' ')
            url = client.torrent_stream_url(f['sid'], f['fileid'])
            call.append(url)
            if sys.stdout.isatty() and args.command:
                print 'running: %s' % ' '.join(call)
                try:
                    subprocess.call(call)
                except OSError as e:
                    error(e.strerror)
            elif sys.stdout.isatty():
                print '%s: %s' % (f['name'], url)

if __name__ == '__main__':
    main()
