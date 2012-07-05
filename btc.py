#! /usr/bin/env python

import re, os
import json, sys
import argparse
import fileinput
from btclient import BTClient

encoder = json.JSONEncoder(indent = 2)
decoder = json.JSONDecoder()

config_file = os.path.join(os.getenv('HOME'), '.btc')
config = {}
if os.path.exists(config_file):
    _c = open(config_file, 'r')
    config = decoder.decode(_c.read())
    _c.close()

host = "127.0.0.1"
port = 8080
if 'host' in config:
    host = config['host']
if 'port' in config:
    port = config['port']

client = BTClient(decoder, host, port)

def error(msg, die=True):
    sys.stderr.write('%s: error: %s\n' % (os.path.basename(sys.argv[0]), msg))
    if die:
        exit(1)

def warning(msg):
    sys.stderr.write('%s: warning: %s\n' % (os.path.basename(sys.argv[0]), msg))

def usage():
    app = os.path.basename(sys.argv[0]).split(' ')[0]

    commands = [
        ('list', 'list client torrents'),
        ('files', 'list files of torrents'),
        ('add', 'add torrent to client'),
        ('remove', 'remove torrent'),
        ('start', 'start torrent'),
        ('stop', 'stop torrent'),
        ('download', 'download torrent file locally'),
        ('stream', 'stream torrent file locally'),
        ('wait', 'wait for torrent download to complete'),
        ('filter', 'filter elements of a list'),
        ('sort', 'sort elements of a list'),
    ]

    print 'usage: %s <command> [<args>]' % app
    print
    print 'Commands are:'
    for (command, info) in commands:
        print '    %-10s: %s' % (command, info)

def list_to_dict(l, key):
    d = {}
    for t in l:
        d[t[key]] = dict(t)
        del d[t[key]][key]
    return d

def dict_to_list(d, key):
    l = []
    for k in d:
        new = dict(d[k])
        new[key] = k
        l.append(new)
    return l

def main():
    if len(sys.argv) < 2:
        usage()
        exit(1)

    try:
        module = __import__(sys.argv[1])
        # FIXME: another module can have a main attribute
        #        import only modules from btc...
        if 'main' not in dir(module):
            raise ImportError()
    except ImportError:
        error('no such command: %s' % sys.argv[1], False)
        print
        usage()
        exit(1)

    sys.argv[0] += ' %s' % sys.argv[1]
    del sys.argv[1]
    module.main()

    exit(0)

if __name__ == "__main__":
    main()
