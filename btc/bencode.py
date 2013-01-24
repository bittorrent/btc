import sys

try:
    unicode
except NameError:
    unicode = str

try:
    long
except NameError:
    long = int

if bytes == str:
    def f(s, *args, **kwargs):
        return str(s)
    bytes = f

class BTFailure(Exception):
    pass

def bytes_index(s, pattern, start):
    if sys.version_info[0] == 2:
        return s.index(pattern, start)

    assert len(pattern) == 1
    for i, e in enumerate(s[start:]):
        if e == ord(pattern):
            return i + start
    raise ValueError('substring not found')

def ord_(s):
    if sys.version_info[0] == 3:
        return ord(s)
    return s

def chr_(s):
    if sys.version_info[0] == 3:
        return chr(s)
    return s

def decode_int(x, f):
    f += 1
    newf = bytes_index(x, 'e', f)
    n = int(x[f:newf])
    if x[f] == ord_('-'):
        if x[f + 1] == ord_('0'):
            raise ValueError
    elif x[f] == ord_('0') and newf != f+1:
        raise ValueError
    return (n, newf+1)

def decode_string(x, f):
    colon = bytes_index(x, ':', f)
    n = int(x[f:colon])
    if x[f] == ord_('0') and colon != f+1:
        raise ValueError
    colon += 1
    return (x[colon:colon+n], colon+n)

def decode_list(x, f):
    r, f = [], f+1
    while x[f] != ord_('e'):
        v, f = decode_func[chr_(x[f])](x, f)
        r.append(v)
    return (r, f + 1)

def decode_dict(x, f):
    r, f = {}, f+1
    while x[f] != ord_('e'):
        k, f = decode_string(x, f)
        r[k], f = decode_func[chr_(x[f])](x, f)
    return (r, f + 1)

decode_func = {}
decode_func['l'] = decode_list
decode_func['d'] = decode_dict
decode_func['i'] = decode_int
decode_func['0'] = decode_string
decode_func['1'] = decode_string
decode_func['2'] = decode_string
decode_func['3'] = decode_string
decode_func['4'] = decode_string
decode_func['5'] = decode_string
decode_func['6'] = decode_string
decode_func['7'] = decode_string
decode_func['8'] = decode_string
decode_func['9'] = decode_string

def bdecode(x):
    try:
        r, l = decode_func[chr_(x[0])](x, 0)
    except (IndexError, KeyError, ValueError):
        raise
        raise BTFailure("not a valid bencoded string")
    if l != len(x):
        raise BTFailure("invalid bencoded value (data after valid prefix)")
    return r

class Bencached(object):

    __slots__ = ['bencoded']

    def __init__(self, s):
        self.bencoded = s

def encode_bencached(x,r):
    r.append(x.bencoded)

def encode_int(x, r):
    r.append(b'i')
    r.append(bytes(str(x), 'ascii'))
    r.append(b'e')

def encode_bool(x, r):
    if x:
        encode_int(1, r)
    else:
        encode_int(0, r)

def encode_string(x, r):
    r.extend((bytes(str(len(x)), 'ascii'), b':', x))

def encode_list(x, r):
    r.append(b'l')
    for i in x:
        encode_func[type(i)](i, r)
    r.append(b'e')

def encode_dict(x,r):
    r.append(b'd')
    ilist = list(x.items())
    ilist.sort()
    for k, v in ilist:
        r.extend((bytes(str(len(k)), 'ascii'), b':', k))
        encode_func[type(v)](v, r)
    r.append(b'e')

encode_func = {}
encode_func[Bencached] = encode_bencached
encode_func[int] = encode_int
encode_func[long] = encode_int
encode_func[str] = encode_string
encode_func[bytes] = encode_string
encode_func[unicode] = encode_string
encode_func[list] = encode_list
encode_func[tuple] = encode_list
encode_func[dict] = encode_dict

try:
    from types import BooleanType
    encode_func[BooleanType] = encode_bool
except ImportError:
    pass

def bencode(x):
    r = []
    encode_func[type(x)](x, r)
    return b''.join(r)
