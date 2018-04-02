# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import base64
import re
import xml.dom.minidom

import Cryptodome.Cipher.AES

from module.util.encoding import smart_bytes
from ..internal.Container import Container
from ..internal.misc import encode


class DLC(Container):
    __name__ = "DLC"
    __type__ = "container"
    __version__ = "0.34"
    __status__ = "testing"

    __pattern__ = r'(.+\.dlc|[\w\+^_]+==[\w\+^_/]+==)$'
    __config__ = [("activated", "bool", "Activated", True),
                  ("use_premium", "bool", "Use premium account if available", True),
                  ("folder_per_package", "Default;Yes;No", "Create folder for each package", "Default")]

    __description__ = """DLC container decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("RaNaN", "RaNaN@pyload.org"),
                   ("spoob", "spoob@pyload.org"),
                   ("mkaay", "mkaay@mkaay.de"),
                   ("Schnusch", "Schnusch@users.noreply.github.com"),
                   ("Walter Purcaro", "vuolter@gmail.com"),
                   ("GammaC0de", "nitzo2001[AT]yahoo[DOT]com")]

    KEY = "cb99b5cbc24db398"
    IV = "9bc24cb995cb8db3"
    API_URL = "http://service.jdownloader.org/dlcrypt/service.php?srcType=dlc&destType=pylo&data=%s"

    def decrypt(self, pyfile):
        fs_filename = encode(pyfile.url)
        with open(fs_filename) as dlc:
            data = dlc.read().strip()

        data += '=' * (-len(data) % 4)

        dlc_key = data[-88:]
        dlc_data = base64.b64decode(smart_bytes(data[:-88]))
        dlc_content = self.load(self.API_URL % dlc_key)

        try:
            rc = re.search(r'<rc>(.+)</rc>', dlc_content, re.S).group(1)
            decoded_rc = base64.b64decode(smart_bytes(rc))[:16]

        except AttributeError:
            self.fail(_("Container is corrupted"))

        key = iv = Cryptodome.Cipher.AES.new(self.KEY, Cryptodome.Cipher.AES.MODE_CBC, self.IV).decrypt(decoded_rc)

        self.data = base64.b64decode(smart_bytes(
            Cryptodome.Cipher.AES.new(key, Cryptodome.Cipher.AES.MODE_CBC, iv).decrypt(dlc_data)
        ))

        self.packages = [(name or pyfile.name, links, name or pyfile.name)
                         for name, links in self.get_packages()]

    def get_packages(self):
        root = xml.dom.minidom.parseString(self.data).documentElement
        content = root.getElementsByTagName("content")[0]
        return self.parse_packages(content)

    def parse_packages(self, startNode):
        return [
            (
                base64.b64decode(smart_bytes(node.getAttribute("name"))),
                self.parse_links(node),
            )
            for node in startNode.getElementsByTagName("package")
        ]

    def parse_links(self, startNode):
        return [
            base64.b64decode(smart_bytes(node.getElementsByTagName("url")[0].firstChild.data))
            for node in startNode.getElementsByTagName("file")
        ]
