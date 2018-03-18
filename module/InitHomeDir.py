#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.

    @author: RaNaN

	This modules inits working directories and global variables, pydir and homedir
"""

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import sys
from os import (
    chdir,
    makedirs,
    path,
)
from os.path import join
from sys import (
    argv,
    platform,
)

from six.moves import builtins

builtins.owd = path.abspath("") #original working directory
builtins.pypath = path.abspath(path.join(__file__, "..", ".."))

sys.path.append(join(pypath, "module", "lib"))

homedir = ""

if platform == 'nt':
    homedir = path.expanduser("~")
    if homedir == "~":
        import ctypes

        CSIDL_APPDATA = 26
        _SHGetFolderPath = ctypes.windll.shell32.SHGetFolderPathW
        _SHGetFolderPath.argtypes = [ctypes.wintypes.HWND,
                                     ctypes.c_int,
                                     ctypes.wintypes.HANDLE,
                                     ctypes.wintypes.DWORD, ctypes.wintypes.LPCWSTR]

        path_buf = ctypes.wintypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        result = _SHGetFolderPath(0, CSIDL_APPDATA, 0, 0, path_buf)
        homedir = path_buf.value
else:
    homedir = path.expanduser("~")

builtins.homedir = homedir

args = " ".join(argv[1:])

# dirty method to set configdir from commandline arguments
if "--configdir=" in args:
    pos = args.find("--configdir=")
    end = args.find("-", pos + 12)

    if end == -1:
        configdir = args[pos + 12:].strip()
    else:
        configdir = args[pos + 12:end].strip()
elif path.exists(path.join(pypath, "module", "config", "configdir")):
    f = open(path.join(pypath, "module", "config", "configdir"), "rb")
    c = f.read().strip()
    f.close()
    configdir = path.join(pypath, c)
else:
    if platform in ("posix", "linux2"):
        configdir = path.join(homedir, ".pyload")
    else:
        configdir = path.join(homedir, "pyload")

if not path.exists(configdir):
    makedirs(configdir, 0o700)

builtins.configdir = configdir
chdir(configdir)

#print "Using %s as working directory." % configdir
