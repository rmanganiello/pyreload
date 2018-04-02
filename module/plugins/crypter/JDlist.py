# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import base64

from module.util.encoding import smart_bytes

from ..internal.Crypter import Crypter


class JDlist(Crypter):
    __name__ = "JDlist"
    __type__ = "crypter"
    __version__ = "0.06"
    __status__ = "testing"

    __pattern__ = r'jdlist://(?P<LIST>[\w\+^_]+==)'
    __config__ = [("activated", "bool", "Activated", True),
                  ("use_premium", "bool", "Use premium account if available", True),
                  ("folder_per_package", "Default;Yes;No", "Create folder for each package", "Default")]

    __description__ = """JDlist decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("Walter Purcaro", "vuolter@gmail.com")]

    def decrypt(self, pyfile):
        self.links.extend(
            base64.b64decode(smart_bytes(self.info['pattern']['LIST'])).split(',')
        )
