# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.utils import simplejson as json
import random
import base64
def generate_random_from_vschar_set(length=30):
    rand = random.SystemRandom()
    return ''.join(rand.choice('abcdefghijklmnopqrstuvwxyz'
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                               '0123456789') for x in range(length))

def HttpResponseJson(json_obj):
    return HttpResponse(json.dumps(json_obj),content_type="application/json")


#http://stackoverflow.com/questions/2817869/error-unable-to-find-vcvarsall-bat
#https://www.dlitz.net/software/pycrypto/api/current/
#http://www.voidspace.org.uk/python/modules.shtml#pycrypto
import Crypto.Random
from Crypto.Cipher import AES
import hashlib

# salt size in bytes
SALT_SIZE = 16

# number of iterations in the key generation
NUMBER_OF_ITERATIONS = 20

# the size multiple required for AES
AES_MULTIPLE = 16

def generate_key(password, salt, iterations):
    assert iterations > 0

    key = password + salt

    for i in range(iterations):
        key = hashlib.sha256(key).digest()

    return key


def pad_text(text, multiple):
    extra_bytes = len(text) % multiple

    padding_size = multiple - extra_bytes

    padding = chr(padding_size) * padding_size

    padded_text = text + padding

    return padded_text

def unpad_text(padded_text):
    padding_size = ord(padded_text[-1])

    text = padded_text[:-padding_size]

    return text


def encrypt(plaintext, password):
    salt = Crypto.Random.get_random_bytes(SALT_SIZE)

    key = generate_key(password, salt, NUMBER_OF_ITERATIONS)

    cipher = AES.new(key, AES.MODE_ECB)

    padded_plaintext = pad_text(plaintext, AES_MULTIPLE)

    ciphertext = cipher.encrypt(padded_plaintext)

    ciphertext_with_salt = salt + ciphertext

    return base64.urlsafe_b64encode(ciphertext_with_salt)
    #return base64.urlsafe_b64encode(ciphertext_with_salt)

    #return encrypt(ciphertext_with_salt, password2)

def decrypt(ciphertext, password):
    ciphertext = base64.urlsafe_b64decode(ciphertext)

    salt = ciphertext[0:SALT_SIZE]

    ciphertext_sans_salt = ciphertext[SALT_SIZE:]

    key = generate_key(password, salt, NUMBER_OF_ITERATIONS)

    cipher = AES.new(key, AES.MODE_ECB)

    padded_plaintext = cipher.decrypt(ciphertext_sans_salt)

    plaintext = unpad_text(padded_plaintext)

    return plaintext
