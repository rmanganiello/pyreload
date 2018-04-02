# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import base64
import binascii
import re

import Cryptodome.Cipher.AES

from module.util.encoding import smart_bytes
from ..internal.Container import Container
from ..internal.misc import encode


class RSDF(Container):
    __name__ = "RSDF"
    __type__ = "container"
    __version__ = "0.39"
    __status__ = "testing"

    __pattern__ = r'.+\.rsdf$'
    __config__ = [("activated", "bool", "Activated", True),
                  ("use_premium", "bool", "Use premium account if available", True),
                  ("folder_per_package", "Default;Yes;No", "Create folder for each package", "Default")]

    __description__ = """RSDF container decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("RaNaN", "RaNaN@pyload.org"),
                   ("spoob", "spoob@pyload.org"),
                   ("Walter Purcaro", "vuolter@gmail.com")]

    KEY = "8C35192D964DC3182C6F84F3252239EB4A320D2500000000"
    IV = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"

    def decrypt(self, pyfile):
        KEY = binascii.unhexlify(self.KEY)
        IV = binascii.unhexlify(self.IV)

        iv = Cryptodome.Cipher.AES.new(KEY, Cryptodome.Cipher.AES.MODE_ECB).encrypt(IV)
        cipher = Cryptodome.Cipher.AES.new(KEY, Cryptodome.Cipher.AES.MODE_CFB, iv)

        try:
            fs_filename = encode(pyfile.url)
            with open(fs_filename, 'r') as rsdf:
                data = rsdf.read()

        except IOError as e:
            self.fail(e.message)

        if re.search(r'<title>404 - Not Found</title>', data):
            pyfile.setStatus("offline")

        else:
            try:
                raw_links = binascii.unhexlify(
                    ''.join(data.split())).splitlines()

            except TypeError:
                self.fail(_("Container is corrupted"))

            for link in raw_links:
                if not link:
                    continue
                link = cipher.decrypt(base64.b64decode(smart_bytes(link))).replace('CCF: ', '')
                self.links.append(link)
