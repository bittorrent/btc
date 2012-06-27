#! /usr/bin/env python

import httplib, mimetypes, base64

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

def post_multipart(host, selector, fields, files, username, password):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTPConnection(host)
    headers = { 'Authorization': 'Basic %s' % base64string,
                'Content-Type': content_type,
                'Content-Length': str(len(body)) }
    h.request('POST', selector, body, headers)
    return h.getresponse().read()

def get(host, selector, username, password):
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    h = httplib.HTTPConnection(host)
    headers = { 'Authorization': 'Basic %s' % base64string }
    h.request('GET', selector, "", headers)
    return h.getresponse().read()
