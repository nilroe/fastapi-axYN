import hashlib

def crypt(object):
    enc = hashlib.sha256(object.encode())
    return enc.hexdigest();

a = crypt('repr0gest)')

def removeacccents(object):
    stri = str(object)
    stri = stri.replace('á','a')
    stri = stri.replace('é','e')
    stri = stri.replace('í','i')
    stri = stri.replace('ó','o')
    stri = stri.replace('ú','u')
    stri = stri.replace('ç','c')
    stri = stri.replace('Á','A')
    stri = stri.replace('É','E')
    stri = stri.replace('Í','I')
    stri =  stri.replace('Ó','O')
    stri = stri.replace('Ú','U')
    stri = stri.replace('Ç','C')

    return stri;