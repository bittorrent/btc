BTC
===

This project enables you to control uTorrent from the command line.

Installation
------------

BTC requires python 2.6.x or 2.7.x and can be installed using pip:

    $ pip install -U https://github.com/bittorrent/btc/tarball/master

If you were to make changes to the source code, which is welcome, you
can fork the git repository on Github and install a development setup
doing:

    $ python setup.py develop

You can then use pull requests if you want your changes to be
integrated.

Configuration
-------------

Located in your home folder, the settings file should be named `.btc`.
This file has to hold a valid JSON dictionary. In order to have BTC
talk to uTorrent we need to set `host`, `port`, `username` and
`password` settings properly. All these settings have default values
and an empty settings file will be equivalent to:

    default = {
      'host': '127.0.0.1',
      'port': 8080,
      'username': 'admin',
      'password': ''
    }

In order to keep this file clean you can use `btc set` to change
settings.

    $ btc set host 192.168.1.10
    $ btc set port 8889

If you want to remove a setting and get the default back, you can use
the `--delete` option to get rid of it.

    $ btc set --delete host

Usage
-----

BTC is made to behave in a way that might surprise you at first.  It
is made to be piped into itself. What does it mean? When you pipe a
command into another, say you type `ls | grep bittorrent`, the output
of `ls` is going to be used as the input of `grep` and `grep` will
output only the lines with the word `bittorrent`. BTC leverages this
mecanism as its core way of processing data and requesting
actions. Everything beggins with the `list` command.

    $ btc list
    [
      {
        "name": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "sid": "5deab0a",
        "dl_rate": 0,
        "done": 815997472,
        "peers_connected": 0,
        "seeds_connected": 0,
        "size": 815997472,
        "state": "SEEDING",
        "ul_rate": 0
      },
      {
        "name": "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "hash": "779E32E8D82521A3472FE6F93C0B29984A7FB411",
        "sid": "5d6264e",
        "dl_rate": 0,
        "done": 477507449,
        "peers_connected": 0,
        "seeds_connected": 0,
        "size": 477507449,
        "state": "SEEDING",
        "ul_rate": 0
      }
    ]

This command queries uTorrent for the list of all its torrents, and
BTC outputs them, using JSON format, as a list of dictionaries each
dictionary being a torrent. Each torrent is reported with its name and
hash but other information such as `peers_connected` or current
`state` and so on. This is nice, but what next? This command can then
be piped to other commands in order to filter the information you want
and have BTC perform the operations you want on your uTorrent
client. Let's say you want to stop the torrent named with all these
'A's.

    $ btc list "A*" | btc stop

This torrent is not going to be seeded anymore by uTorrent. Don't
worry, you can restart it using the `start` command. This is the right
moment to mention that `btc list` takes an optional argument which
filters all the torrents by name allowing glob syntax. The
`--case-sensitive` or the shorter `-s` options can be used to enforce
case sensitivity. Some of you might think that it is a lot more
complicated than doing `btc stop "A*"`. Fair enough, but what if you
only want to stop torrents with a `dl_rate` of zero?

    $ btc list | btc filter --key dl_rate --numeric-equals 0 | btc stop

As simple as that. The `filter` command is here to help you select the
entries you want and reject the other ones. It can be used to filter
anything BTC outputs, not only torrents, but we will see that
afterwards. The `filter` command can have multiple arguments (see `btc
filter --help`) such as `--nth N` which select the N-th entry in a
list or `--first N` which takes the N first entries of the
list. Given a key supplied with `--key` each entry is going to be
selected if:

    $ btc list | btc filter --key KEY "X*"  # it matches a string, supporting glob syntax
    $ btc list | btc filter --key KEY --numeric-equals X  # its numeric value equals X
    $ btc list | btc filter --key KEY --numeric-differs X # its numeric value differs from X
    $ btc list | btc filter --key KEY --less X    # its numeric value is less than X
    $ btc list | btc filter --key KEY --greater X # its numeric value is greater than X
    $ btc list | btc filter --key KEY --true      # it is the boolean value true
    $ btc list | btc filter --key KEY --false     # it is the boolean value false
    ...

Multiple filter commands can be piped one after the other for the
output to match exactly what you want.

What about files? A torrent can have multiple files and you can list
them using the `files` command. Hence for one or many torrents
outputed by `btc list`, `btc files` lists the files inside this or
these torrents.

    $ btc list "A*" | btc files
    [
      {
        "name": "audio_1.mp3",
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "sid": "5deab0a",
        "fileid": 0,
        "downloaded": 6579667,
        "priority": 2,
        "size": 6579667
      },
      {
        "name": "image_1.jpeg",
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "sid": "5deab0a",
        "fileid": 1,
        "downloaded": 384077,
        "priority": 2,
        "size": 384077
      },
      {
        "name": "video_6.mpg",
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "sid": "5deab0a",
        "fileid": 2,
        "downloaded": 809033728,
        "priority": 2,
        "size": 809033728
      }
    ]

This lists all the files of the torrent(s) given in input. The
`filter` command can be used here again to select some of these
files. But let's introduce the `sort` command. It allows you to sort
the results by simply piping them to `btc sort`. By default, giving it
no arguments, it is going to sort the entries by name. Another key can
also be specified with the option `--key` if you were to sort by size
for instance. You can also reverse the sort by using the option
`--reverse`.

    $ btc list | btc files | btc sort
    [
      {
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "name": "audio_1.mp3",
        "priority": 2,
        "downloaded": 6579667,
        "sid": "5deab0a",
        "size": 6579667,
        "fileid": 0
      },
      {
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "name": "image_1.jpeg",
        "priority": 2,
        "downloaded": 384077,
        "sid": "5deab0a",
        "size": 384077,
        "fileid": 1
      },
      {
        "hash": "779E32E8D82521A3472FE6F93C0B29984A7FB411",
        "name": "image_2.jpg",
        "priority": 2,
        "downloaded": 3386455,
        "sid": "5d6264e",
        "size": 3386455,
        "fileid": 0
      },
      {
        "hash": "779E32E8D82521A3472FE6F93C0B29984A7FB411",
        "name": "video_14.avi",
        "priority": 2,
        "downloaded": 474120994,
        "sid": "5d6264e",
        "size": 474120994,
        "fileid": 1
      },
      {
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "name": "video_6.mpg",
        "priority": 2,
        "downloaded": 809033728,
        "sid": "5deab0a",
        "size": 809033728,
        "fileid": 2
      }
    ]

    $ btc list | btc files | btc sort --key size
    [
      {
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "name": "image_1.jpeg",
        "priority": 2,
        "downloaded": 384077,
        "sid": "5deab0a",
        "size": 384077,
        "fileid": 1
      },
      {
        "hash": "779E32E8D82521A3472FE6F93C0B29984A7FB411",
        "name": "image_2.jpg",
        "priority": 2,
        "downloaded": 3386455,
        "sid": "5d6264e",
        "size": 3386455,
        "fileid": 0
      },
      {
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "name": "audio_1.mp3",
        "priority": 2,
        "downloaded": 6579667,
        "sid": "5deab0a",
        "size": 6579667,
        "fileid": 0
      },
      {
        "hash": "779E32E8D82521A3472FE6F93C0B29984A7FB411",
        "name": "video_14.avi",
        "priority": 2,
        "downloaded": 474120994,
        "sid": "5d6264e",
        "size": 474120994,
        "fileid": 1
      },
      {
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "name": "video_6.mpg",
        "priority": 2,
        "downloaded": 809033728,
        "sid": "5deab0a",
        "size": 809033728,
        "fileid": 2
      }
    ]

    $ btc list | btc files | btc sort --key size --reverse
    [
      {
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "name": "video_6.mpg",
        "priority": 2,
        "downloaded": 809033728,
        "sid": "5deab0a",
        "size": 809033728,
        "fileid": 2
      },
      {
        "hash": "779E32E8D82521A3472FE6F93C0B29984A7FB411",
        "name": "video_14.avi",
        "priority": 2,
        "downloaded": 474120994,
        "sid": "5d6264e",
        "size": 474120994,
        "fileid": 1
      },
      {
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "name": "audio_1.mp3",
        "priority": 2,
        "downloaded": 6579667,
        "sid": "5deab0a",
        "size": 6579667,
        "fileid": 0
      },
      {
        "hash": "779E32E8D82521A3472FE6F93C0B29984A7FB411",
        "name": "image_2.jpg",
        "priority": 2,
        "downloaded": 3386455,
        "sid": "5d6264e",
        "size": 3386455,
        "fileid": 0
      },
      {
        "hash": "45097EB957FD45EE657A442B16F702251CBB8E35",
        "name": "image_1.jpeg",
        "priority": 2,
        "downloaded": 384077,
        "sid": "5deab0a",
        "size": 384077,
        "fileid": 1
      }
    ]

You can also download on your disk some files using the `download`
command. Piping a list of files to `btc download` will download them
to the directory from which BTC is run. To change the output directory
you can use the `--directory` option. If you are dealing with a single
file you can also rename it using the `--output` option. Last but not
least, if uTorrent is running on Windows you need to add the
`--windows` option so that the backslashes will be converted to
forward slashes.

    $ btc list | btc files | btc download
    downloading: ./audio_1.mp3
    downloading: ./image_1.jpeg
    downloading: ./image_2.jpg
    downloading: ./video_14.avi
    downloading: ./video_6.mpg

    $ btc list | btc files | btc download --directory /tmp
    downloading: /tmp/audio_1.mp3
    downloading: /tmp/image_1.jpeg
    downloading: /tmp/image_2.jpg
    downloading: /tmp/video_14.avi
    downloading: /tmp/video_6.mpg

    $ btc list | btc files | btc filter --nth 1 | btc download --output /tmp/file
    downloading: /tmp/file

Want to stream? No problem, use `btc stream`. With files as input it
will run a stream command with the appropriate streaming url. By
default it outputing the stream urls to your terminal. You can provide
a streaming command using the `--command` option.

    $ btc list | btc files | btc stream
    btc stream: warning: no stream command specified, outputing streaming links
    audio_1.mp3: http://admin:@127.0.0.1:8080/proxy?sid=5deab0a&file=0&service=DOWNLOAD&qos=0&disposition=inline
    image_1.jpeg: http://admin:@127.0.0.1:8080/proxy?sid=5deab0a&file=1&service=DOWNLOAD&qos=0&disposition=inline
    image_2.jpg: http://admin:@127.0.0.1:8080/proxy?sid=5d6264e&file=0&service=DOWNLOAD&qos=0&disposition=inline
    video_14.avi: http://admin:@127.0.0.1:8080/proxy?sid=5d6264e&file=1&service=DOWNLOAD&qos=0&disposition=inline
    video_6.mpg: http://admin:@127.0.0.1:8080/proxy?sid=5deab0a&file=2&service=DOWNLOAD&qos=0&disposition=inline
    $ btc list | btc files | btc filter --nth 1 | btc stream --command mplayer
    running: mplayer http://admin:@127.0.0.1:8080/proxy?sid=5deab0a&file=0&service=DOWNLOAD&qos=0&disposition=inline
    $ btc list | btc files | btc stream --command mplayer
    running: mplayer http://admin:@127.0.0.1:8080/proxy?sid=5deab0a&file=0&service=DOWNLOAD&qos=0&disposition=inline
    running: mplayer http://admin:@127.0.0.1:8080/proxy?sid=5deab0a&file=1&service=DOWNLOAD&qos=0&disposition=inline
    running: mplayer http://admin:@127.0.0.1:8080/proxy?sid=5d6264e&file=0&service=DOWNLOAD&qos=0&disposition=inline
    running: mplayer http://admin:@127.0.0.1:8080/proxy?sid=5d6264e&file=1&service=DOWNLOAD&qos=0&disposition=inline
    running: mplayer http://admin:@127.0.0.1:8080/proxy?sid=5deab0a&file=2&service=DOWNLOAD&qos=0&disposition=inline

If you want to play all the files using a single instance of the
command you may use the option `--together` which has the following
behavior:

    $ btc list | btc files | btc stream --command mplayer --together
    running: mplayer http://admin:@127.0.0.1:8080/proxy?sid=5deab0a&file=0&service=DOWNLOAD&qos=0&disposition=inline http://admin:@127.0.0.1:8080/proxy?sid=5deab0a&file=1&service=DOWNLOAD&qos=0&disposition=inline http://admin:@127.0.0.1:8080/proxy?sid=5d6264e&file=0&service=DOWNLOAD&qos=0&disposition=inline http://admin:@127.0.0.1:8080/proxy?sid=5d6264e&file=1&service=DOWNLOAD&qos=0&disposition=inline http://admin:@127.0.0.1:8080/proxy?sid=5deab0a&file=2&service=DOWNLOAD&qos=0&disposition=inline

Here is the way to add a torrent by url or using a file on your
computer:

    $ btc add http://www.clearbits.net/get/547-home-2009.torrent
    $ btc add "home project - home 2009.torrent"

And then you can remove the torrent from your downloads keeping or not
the torrent file and dropping or not the data:

    $ btc list "Home Project - Home 2009" | btc remove
    $ btc list "Home Project - Home 2009" | btc remove --keep-torrent
    $ btc list "Home Project - Home 2009" | btc remove --drop-data
    $ btc list "Home Project - Home 2009" | btc remove --keep-torrent --drop-data

Finally the `wait` command simply waits for a torrent to complete. You
can use that to run a command when the torrent is complete, shutdown
for instance...

    $ btc list "Home Project - Home 2009" | btc wait && shutdown
