import hashlib

def crypt(object):
    enc = hashlib.sha256(object.encode())
    return enc.hexdigest();

a = crypt('repr0gest)')