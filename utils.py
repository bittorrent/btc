#! /usr/bin/env python

import httplib2, mimetypes, base64
import re

class Cookie (dict):
    pattern = re.compile(r'(.*?)=(.*?)(?:;\s*|$)')

    def __init__(self, wevs={}):
        if isinstance(wevs, basestring):
            wevs = self.pattern.findall(wevs)
        super(Cookie, self).__init__(wevs)

    def __str__(self):
        return '; '.join('{0}={1}'.format(k,v) for k,v in self.iteritems())

    def update(self, new):
        super(Cookie, self).update(Cookie(new))

class HTTPError (Exception):
    pass

cookie = Cookie()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % mimetypes.guess_type(filename)[0] or 'application/octet-stream')
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def httpize(url):
    if not url.startswith('http'):
        return 'http://{0}'.format(url)
    return url

def post_multipart(host, selector, fields, files, username, password):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib2.Http()
    headers = { 'Authorization': 'Basic %s' % base64string,
                'Content-Type': content_type,
                'Content-Length': str(len(body)),
                'Cookie': str(cookie) }

    host = httpize(host)
    response, content = h.request(host + selector, method='POST', body=body, headers=headers)

    if response['status'] == '200' and 'set-cookie' in response:
        cookie.update(response['set-cookie'])
    elif response['status'] != '200':
        raise HTTPError(response['status'])

    return content

def get(host, selector="", username=None, password=None):
    if username:
        base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    h = httplib2.Http()
    if username:
        headers = { 'Authorization': 'Basic %s' % base64string,
                    'Cookie': str(cookie) }
    else:
        headers = {}

    host = httpize(host)

    try:
        response, content = h.request(host + selector, headers=headers)
    except httplib2.ServerNotFoundError:
        raise HTTPError('404')

    if response['status'] == '200' and 'set-cookie' in response:
        cookie.update(response['set-cookie'])
    elif response['status'] != '200':
        raise HTTPError(response['status'])

    return content
