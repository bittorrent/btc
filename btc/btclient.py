import re, os
import json, sys
import argparse
import fileinput
import utils

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
        l = re.findall(r"<html><div id='token' style='display:none;'>(.*)</div></html>", response)
        return l[0]

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
                return {}
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

    def torrent_list(self, response):
        response_dict = self.decoder.decode(response)
        response = []
        for torrent_response in response_dict['torrents']:
            torrent_dict = {}
            response.append(torrent_dict)
            torrent_dict['hash'] = str(torrent_response[0].upper())
            torrent_dict['name'] = torrent_response[2]
            torrent_dict['done'] = torrent_response[3] - torrent_response[18]
            torrent_dict['eta'] = torrent_response[10]
            torrent_dict['peers_connected'] = torrent_response[12]
            torrent_dict['seeds_connected'] = torrent_response[14]
            torrent_dict['size'] = torrent_response[3]
            torrent_dict['sid'] = torrent_response[22]
            torrent_dict['ul_rate'] = torrent_response[8]
            torrent_dict['dl_rate'] = torrent_response[9]
	    if torrent_dict['size'] != 0:
                torrent_dict['progress'] = round(100 * float(torrent_dict['done']) / torrent_dict['size'], 2)
            else:
                torrent_dict['progress'] = 0
            state = torrent_response[21]
            state = state.upper()
            state = state.replace('[F] ', '')
            state = state.replace(' ', '_')
            state = re.sub(r'CHECKED.*', 'CHECKING', state)
            state = re.sub(r'ERROR.*', 'ERROR', state)
            torrent_dict['state'] = state
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
                    f['progress'] = round(100 * float(f['downloaded']) / f['size'])
                    response.append(f)
                    i += 1

        return response
