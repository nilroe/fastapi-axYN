import hashlib
import os;
import sys

def crypt_pass(password):
    enc = hashlib.sha256(password.encode())
    return enc.hexdigest();

a = crypt_pass('repr0gest)')
