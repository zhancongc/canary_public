# coding=utf-8
"""
filename: utils.py
author: zhancongc@icloud.com
description: 工具文件，包含MD5的两种计算，int和bytes互转，加密和解密算法
"""

import struct
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def md5sum(strings, is_bin):
    sh = hashlib.md5()
    sh.update(strings)
    if is_bin:
        return sh.digest()
    else:
        return sh.hexdigest()


def int2bytes(number):
    return struct.pack("i", number)


def bytes2int(buffer):
    return struct.unpack("i", buffer)[0]


class Encrypt(object):
    key = 0
    iv = b""
    key_dict = "P%2BViyZLtO^gRT2Huxqx#5VygbflvZx$8mFpX61VWvd;ivPu~XjL`CD7FrIe8=0"
    secret = b""

    def __init__(self, key):
        self.key = key
        self.iv = b"\0"*16
        self.secret = self.init_secret()

    def init_secret(self):
        print("server key is {0}".format(self.key))
        i = 63
        secret = b""
        while i >= 0:
            if self.key & (1 << i):
                if i < len(self.key_dict):
                    secret += self.key_dict[len(self.key_dict) - 1 - i]
            i -= 1
        if len(secret) < 32:
            secret += "a" * (32 - len(secret))
        else:
            secret = secret[:32]
        print("server secret is {0}".format(secret))
        return secret

    @staticmethod
    def add_to_16(text):
        remainder = len(text) % 16
        if remainder:
            add = 16 - remainder
        else:
            add = 0
        text = text + (b'\0' * add)
        return text

    def encrypt(self, text):
        mode = AES.MODE_CBC
        pad_pkcs7_text = pad(text, AES.block_size, style='pkcs7')
        cryptos = AES.new(self.secret, mode, self.iv)
        cipher_text = cryptos.encrypt(pad_pkcs7_text)
        return cipher_text

    def decrypt(self, text):
        mode = AES.MODE_CBC
        cryptos = AES.new(self.secret, mode, self.iv)
        plain_text = cryptos.decrypt(text)
        return plain_text.strip("\0")

