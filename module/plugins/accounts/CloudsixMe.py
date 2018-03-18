# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from ..internal.XFSAccount import XFSAccount


class CloudsixMe(XFSAccount):
    __name__ = "CloudsixMe"
    __type__ = "account"
    __version__ = "0.05"
    __status__ = "testing"

    __description__ = """Cloudsix.me account plugin"""
    __license__ = "GPLv3"
    __authors__ = [("Walter Purcaro", "vuolter@gmail.com")]

    PLUGIN_DOMAIN = "cloudsix.me"
