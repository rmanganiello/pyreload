#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from module.util.encoding import smart_text


def blue(string):
    return "\033[1;34m" + smart_text(string) + "\033[0m"


def green(string):
    return "\033[1;32m" + smart_text(string) + "\033[0m"


def yellow(string):
    return "\033[1;33m" + smart_text(string) + "\033[0m"


def red(string):
    return "\033[1;31m" + smart_text(string) + "\033[0m"


def cyan(string):
    return "\033[1;36m" + smart_text(string) + "\033[0m"


def mag(string):
    return "\033[1;35m" + smart_text(string) + "\033[0m"


def white(string):
    return "\033[1;37m" + smart_text(string) + "\033[0m"


def println(line, content):
    print("\033[" + smart_text(line) + ";0H\033[2K" + content)
