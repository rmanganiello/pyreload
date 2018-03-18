# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from ..internal.DeadHoster import DeadHoster


class MegauploadCom(DeadHoster):
    __name__ = "MegauploadCom"
    __type__ = "hoster"
    __version__ = "0.36"
    __status__ = "stable"

    __pattern__ = r'http://(?:www\.)?megaupload\.com/\?.*&?(d|v)=\w+'
    __config__ = []  # @TODO: Remove in 0.4.10

    __description__ = """Megaupload.com hoster plugin"""
    __license__ = "GPLv3"
    __authors__ = [("spoob", "spoob@pyload.org")]
