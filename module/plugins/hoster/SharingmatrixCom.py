# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from ..internal.DeadHoster import DeadHoster


class SharingmatrixCom(DeadHoster):
    __name__ = "SharingmatrixCom"
    __type__ = "hoster"
    __version__ = "0.06"
    __status__ = "stable"

    __pattern__ = r'http://(?:www\.)?sharingmatrix\.com/file/\w+'
    __config__ = []  # @TODO: Remove in 0.4.10

    __description__ = """Sharingmatrix.com hoster plugin"""
    __license__ = "GPLv3"
    __authors__ = [("jeix", "jeix@hasnomail.de"),
                   ("paulking", None)]
