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
        return self.torrentList(self.send_command("list=1"))

    def add_torrent_url(self, url):
        self.send_command("action=add-url&s=%s" % url)

    def add_torrent_file(self, torrentFilePath):
        torrentFile = open(torrentFilePath, "rb")
        self.send_command("action=add-file", torrent_file=torrentFile.read())
        torrentFile.close()

    def remove_torrent(self, thash, keep_data=True, keep_torrent=False):
        cmd = None
        if keep_data and keep_torrent:
            cmd = "action=remove&hash=%s"
        elif keep_data and not keep_torrent:
            cmd = "action=removetorrent&hash=%s"
        elif keep_torrent and not keep_data:
            cmd = "action=removedata&hash=%s"
        elif not keep_torrent and not keep_data:
            cmd = "action=removedatatorrent&hash=%s"
        self.send_command(cmd % thash)

    def stop_torrent(self, thash):
        self.send_command("action=stop&hash=%s" % thash)

    def start_torrent(self, thash):
        self.send_command("action=start&hash=%s" % thash)

    def torrent_files(self, thash, sids={}):
        if isinstance(thash, list):
            thash = '&hash='.join(thash)
        l = self.send_command("action=getfiles&format=json&hash=%s" % thash)
        return self.filesDict(l, sids)

    def torrent_download_file(self, sid, fileid, name, path='.'):
        cmd = "sid=%s&file=%d&service=DOWNLOAD&qos=0&disposition=inline" % (sid, fileid)
        content = self.send_command(cmd, root='/proxy', token=False)
        filename = os.path.join(path, name)
        f = open(filename, 'w')
        f.write(content)
        f.close()

    def torrent_stream_url(self, sid, fileid):
        return "http://%s:%s@%s:%d/proxy?sid=%s&file=%d&service=DOWNLOAD&qos=0&disposition=inline" % \
          (self.username, self.password, self.host, self.port, sid, fileid)

    def torrentList(self, response):
        responseDict = self.decoder.decode(response)
        response = []
        for torrentResponse in responseDict["torrents"]:
            torrentDict = {}
            response.append(torrentDict)
            torrentDict["hash"] = str(torrentResponse[0].lower())
            torrentDict["name"] = torrentResponse[2]
            torrentDict["dl_rate"] = torrentResponse[9]
            torrentDict["done"] = torrentResponse[3] - torrentResponse[18]
            torrentDict["eta"] = torrentResponse[10]
            torrentDict["peers_connected"] = torrentResponse[12]
            torrentDict["seeds_connected"] = torrentResponse[14]
            torrentDict["size"] = torrentResponse[3]
            torrentDict["sid"] = torrentResponse[22]

            if 0 == torrentResponse[18]:
                torrentDict["state"] = "FINISHED"
            if torrentResponse[1] & 1:
                torrentDict["state"] = "SEEDING"
            elif (torrentResponse[1] & 2) or (torrentResponse[1] & 4):
                torrentDict["state"] = "CHECKING_FILES"
            elif torrentResponse[1] & 1:
                torrentDict["state"] = "DOWNLOADING"
            elif torrentResponse[1] == 128:
                torrentDict["state"] = "QUEUED_FOR_CHECKING"
            elif torrentResponse[1] == 136:
                torrentDict["state"] = "STOPPED"
            elif torrentResponse[1] == 200:
                torrentDict["state"] = "CHECKING_FILES"
            else:
                torrentDict["state"] = "UNKNOWN"

            if torrentResponse[1] & 1 and (not (torrentResponse[1] & 2) and not (torrentResponse[1] & 4)):
                torrentDict["stopped"] = False
            else:
                torrentDict["stopped"] = True

            torrentDict["ul_rate"] = torrentResponse[8]

        return response

    def filesDict(self, response, sids={}):
        responseDict = self.decoder.decode(response)
        response = list()

        h = None
        for e in responseDict["files"]:
            if isinstance(e, unicode):
                h = e.lower()
            elif isinstance(e, list):
                i = 0
                for l in e:
                    f = dict()
                    if h in sids:
                        f['sid'] = sids[h]
                    f['fileid'] = i
                    f['hash'] = h
                    f['name'] = l[0]
                    f['size'] = l[1]
                    f['downloaded'] = l[2]
                    f['priority'] = l[3]
                    f['progress'] = l[4]
                    response.append(f)
                    i += 1

        return response
