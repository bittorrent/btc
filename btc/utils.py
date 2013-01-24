import httplib2, mimetypes, base64, socket
import re

try:
    basestring
except NameError:
    basestring = str

if bytes == str:
    def f(s, *args, **kwargs):
        return str(s)
    bytes = f

class Cookie (dict):
    pattern = re.compile(r'(.*?)=(.*?)(?:;\s*|$)')

    def __init__(self, wevs={}):
        if isinstance(wevs, basestring):
            wevs = self.pattern.findall(wevs)
        super(Cookie, self).__init__(wevs)

    def __str__(self):
        return '; '.join('{0}={1}'.format(k,v) for k,v in self.items())

    def update(self, new):
        super(Cookie, self).update(Cookie(new))

class HTTPError (Exception):
    pass

cookie = Cookie()
timeout = 2

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = b'----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = b'\r\n'
    L = []
    for (key, value) in fields:
        L.append(b'--' + BOUNDARY)
        L.append(bytes('Content-Disposition: form-data; name="%s"' % key, 'ascii'))
        L.append(b'')
        L.append(value)
    for (key, filename, value) in files:
        L.append(b'--' + BOUNDARY)
        L.append(bytes('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename), 'ascii'))
        L.append(bytes('Content-Type: %s' % mimetypes.guess_type(filename)[0] or 'application/octet-stream', 'ascii'))
        L.append(b'')
        L.append(value)
    L.append(b'--' + BOUNDARY + b'--')
    L.append(b'')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY.decode('ascii')
    return content_type, body

def httpize(url):
    if not url.startswith('http'):
        return 'http://{0}'.format(url)
    return url

def make_request(http, *args, **kwargs):
    try:
        return http.request(*args, **kwargs)
    except httplib2.ServerNotFoundError:
        raise HTTPError('404')
    except (socket.timeout, socket.error):
        raise HTTPError('host does not answer')

def post_multipart(host, selector, fields, files, username, password):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    base64string = base64.encodestring(bytes('%s:%s' % (username, password), 'ascii'))[:-1].decode('ascii')
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib2.Http(timeout=timeout)
    headers = { 'Authorization': 'Basic %s' % base64string,
                'Content-Type': content_type,
                'Content-Length': str(len(body)),
                'Cookie': str(cookie) }

    host = httpize(host)
    response, content = make_request(h, host + selector, method='POST', body=body, headers=headers)

    if response['status'] == '200' and 'set-cookie' in response:
        cookie.update(response['set-cookie'])
    elif response['status'] != '200':
        raise HTTPError(response['status'])

    return content.decode('utf-8')

def get(host, selector="", username=None, password=None, utf8=True):
    if username:
        base64string = base64.encodestring(bytes('%s:%s' % (username, password), 'ascii'))[:-1].decode('ascii')
    h = httplib2.Http(timeout=timeout)
    if username:
        headers = { 'Authorization': 'Basic %s' % base64string,
                    'Cookie': str(cookie) }
    else:
        headers = {}

    host = httpize(host)
    response, content = make_request(h, host + selector, headers=headers)

    if response['status'] == '200' and 'set-cookie' in response:
        cookie.update(response['set-cookie'])
    elif response['status'] != '200':
        raise HTTPError(response['status'])

    if utf8:
        return content.decode('utf-8')
    return content
