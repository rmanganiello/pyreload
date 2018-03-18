# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from ..internal.DeadHoster import DeadHoster


class StorageTo(DeadHoster):
    __name__ = "StorageTo"
    __type__ = "hoster"
    __version__ = "0.06"
    __status__ = "stable"

    __pattern__ = r'http://(?:www\.)?storage\.to/get/.+'
    __config__ = []  # @TODO: Remove in 0.4.10

    __description__ = """Storage.to hoster plugin"""
    __license__ = "GPLv3"
    __authors__ = [("mkaay", "mkaay@mkaay.de")]
