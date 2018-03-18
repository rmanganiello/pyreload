# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from ..internal.DeadHoster import DeadHoster


class BillionuploadsCom(DeadHoster):
    __name__ = "BillionuploadsCom"
    __type__ = "hoster"
    __version__ = "0.11"
    __status__ = "stable"

    __pattern__ = r'http://(?:www\.)?billionuploads\.com/\w{12}'
    __config__ = []  # @TODO: Remove in 0.4.10

    __description__ = """Billionuploads.com hoster plugin"""
    __license__ = "GPLv3"
    __authors__ = [("zoidberg", "zoidberg@mujmail.cz")]
