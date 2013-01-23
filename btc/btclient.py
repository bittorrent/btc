import re, os
import json, sys
import argparse
import fileinput
import datetime
from . import utils

class BTClientError(Exception):
    pass

class BTClient:
    def __init__(self, decoder, host='127.0.0.1', port=8080, username='admin', password=''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.decoder = decoder

    def get_token_argument(self):
        response = self.send_command(root='/gui/token.html', token=False)
        m = re.sub(r"<.*?>", "", response)
        if not m:
            raise BTClientError('token authentification problem')
        return str(m)

    def send_command(self, params='', root='/gui/', token=True,
                     torrent_file=None, username=None, password=None):

        if username is None:
            username = self.username
        if password is None:
            password = self.password

        host = '%s:%s' % (self.host, self.port)
        if token:
            token = self.get_token_argument()
            params = 'token=%s&%s' % (token, params)
        if params:
            url = '%s?%s' % (root, params)
        else:
            url = root
        if torrent_file:
            ret = utils.post_multipart(host, url, [('torrent_file', torrent_file)],
                                        [], username, password)
        else:
            ret = utils.get(host, url, username, password)

        try:
            ret_json = json.loads(ret)
            if 'error' in ret_json:
                raise BTClientError(ret_json['error'])
        except BTClientError:
            raise
        except: # Output might not be JSON
            pass

        return ret

    def list_torrents(self):
        return self.torrent_list(self.send_command('list=1'))

    def add_torrent_url(self, url):
        self.send_command('action=add-url&s=%s' % url)

    def add_torrent_file(self, torrent_file_path):
        torrent_file = open(torrent_file_path, 'rb')
        self.send_command('action=add-file', torrent_file=torrent_file.read())
        torrent_file.close()

    def remove_torrent(self, thash, keep_data=True, keep_torrent=False):
        cmd = None
        if keep_data and keep_torrent:
            cmd = 'action=remove&hash=%s'
        elif keep_data and not keep_torrent:
            cmd = 'action=removetorrent&hash=%s'
        elif keep_torrent and not keep_data:
            cmd = 'action=removedata&hash=%s'
        elif not keep_torrent and not keep_data:
            cmd = 'action=removedatatorrent&hash=%s'
        self.send_command(cmd % thash)

    def stop_torrent(self, thash):
        self.send_command('action=stop&hash=%s' % thash)

    def start_torrent(self, thash):
        self.send_command('action=start&hash=%s' % thash)

    def torrent_files(self, thash, sids={}):
        if isinstance(thash, list):
            if len(thash) == 0:
                return []
            thash = '&hash='.join(thash)
        l = self.send_command('action=getfiles&format=json&hash=%s' % thash)
        return self.files_dict(l, sids)

    def torrent_download_file(self, sid, fileid, name, path='.'):
        cmd = 'sid=%s&file=%d&service=DOWNLOAD&qos=0&disposition=inline' % (sid, fileid)
        content = self.send_command(cmd, root='/proxy', token=False)
        filename = os.path.join(path, name)
        f = open(filename, 'w')
        f.write(content)
        f.close()

    def torrent_stream_url(self, sid, fileid):
        return 'http://%s:%s@%s:%d/proxy?sid=%s&file=%d&service=DOWNLOAD&qos=0&disposition=inline' % \
          (self.username, self.password, self.host, self.port, sid, fileid)


    def _get_state(self, status, remaining):
        TFS_STARTED = 1
        # the torrent is checking its file, to figure out which
        # parts of the files we already have
        TFS_CHECKING = 2
        # start the torrent when the file-check completes
        TFS_START_AFTER_CHECK = 4
        # The files in this torrent have been checked. No need
        # to check them again
        TFS_CHECKED = 8
        # An error ocurred
        TFS_ERROR = 16
        # The torrent is paused. i.e. all transfers are suspended
        TFS_PAUSED = 32
        # Auto managed. uTorrent will automatically start and stop
        # the torrent based on the number of active torrents etc.
        TFS_AUTO = 64
        # The .torrent file has been loaded
        TFS_LOADED = 128
        # the torrent is transforming (usually copying data from
        # another torrent in order to download a similar torrent)
        TFS_TRANSFORMING = 256
        # start the torrent when the transformation completes
        TFS_START_AFTER_TRANSFORM = 512

        if status & TFS_ERROR:
            return "ERROR"
        elif status & TFS_CHECKING:
            return "CHECKED"
        elif status & TFS_TRANSFORMING:
            return "TRANSFORMING"
        else:
            if status & TFS_STARTED:
                if status & TFS_PAUSED:
                    return "PAUSED"
                elif status & TFS_AUTO:
                    return "SEEDING" if remaining == 0 else "DOWNLOADING"
                else:
                    return "SEEDING_FORCED" if remaining == 0 else "DOWNLOADING_FORCED"
            else:
                if status & TFS_PAUSED:
                    return "PAUSED"
                elif remaining == 0:
                    return "QUEUED_SEED" if status & TFS_AUTO else "FINISHED"
                else:
                    return "QUEUED" if status & TFS_AUTO else "STOPPED"


    def torrent_list(self, response):
        response_dict = self.decoder.decode(response)
        response = []
        for torrent_response in response_dict['torrents']:
            torrent_dict = {}
            response.append(torrent_dict)
            torrent_dict['hash'] = str(torrent_response[0].upper())
            torrent_dict['state_code'] = torrent_response[1]
            torrent_dict['name'] = torrent_response[2]
            torrent_dict['size'] = torrent_response[3]
            torrent_dict['progress'] = round(torrent_response[4] / 10., 2)
            torrent_dict['downloaded'] = torrent_response[5]
            torrent_dict['uploaded'] = torrent_response[6]
            torrent_dict['ratio'] = torrent_response[7]
            torrent_dict['upload_rate'] = torrent_response[8]
            torrent_dict['downloadl_rate'] = torrent_response[9]
            torrent_dict['eta'] = torrent_response[10]
            torrent_dict['label'] = torrent_response[11]
            torrent_dict['peers_connected'] = torrent_response[12]
            torrent_dict['peers'] = torrent_response[13]
            torrent_dict['seeds_connected'] = torrent_response[14]
            torrent_dict['seeds'] = torrent_response[15]
            torrent_dict['avail_factor'] = torrent_response[16]
            torrent_dict['order'] = torrent_response[17]
            torrent_dict['remaining'] = torrent_response[18]
            torrent_dict['download_url'] = torrent_response[19]
            torrent_dict['feed_url'] = torrent_response[20]
            torrent_dict['sid'] = torrent_response[22]
            torrent_dict['date_added'] = '%s' % datetime.datetime.fromtimestamp(torrent_response[23])
            torrent_dict['date_completed'] = '%s' % datetime.datetime.fromtimestamp(torrent_response[24])
            torrent_dict['folder'] = torrent_response[26]
            torrent_dict['state'] = self._get_state(torrent_response[1], torrent_dict['remaining'])

        return response

    def files_dict(self, response, sids={}):
        response_dict = self.decoder.decode(response)
        response = list()

        h = None
        for e in response_dict['files']:
            if isinstance(e, unicode):
                h = e.upper()
            elif isinstance(e, list):
                i = 0
                for l in e:
                    f = dict()
                    if h in sids:
                        f['sid'] = sids[h]

                    f['fileid'] = i
                    f['hash'] = h.upper()
                    f['name'] = l[0]
                    f['size'] = l[1]
                    f['downloaded'] = l[2]
                    f['priority'] = l[3]

                    f['streamable'] = l[4]
                    f['encoded_rate'] = l[5]
                    f['duration'] = l[6]
                    f['width'] = l[7]
                    f['height'] = l[8]
                    f['time_to_play'] = l[9]

                    f['progress'] = round(100. * l[2] / l[1], 2)
                    response.append(f)
                    i += 1

        return response
