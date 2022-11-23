# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import sys
import tarfile

from .Extractor import (
    ArchiveError,
    CRCError,
    Extractor,
)
from .misc import encode


class UnTar(Extractor):
    __name__ = "UnTar"
    __type__ = "extractor"
    __version__ = "0.05"
    __status__ = "stable"

    __description__ = """TAR extractor plugin"""
    __license__ = "GPLv3"
    __authors__ = [("Walter Purcaro", "vuolter@gmail.com")]

    VERSION = "%s.%s.%s" % (sys.version_info[0],
                            sys.version_info[1],
                            sys.version_info[2])

    @classmethod
    def isarchive(cls, filename):
        try:
            return tarfile.is_tarfile(encode(filename))
        except:
            return False

    @classmethod
    def find(cls):
        return True

    def list(self, password=None):
        with tarfile.open(self.filename) as t:
            self.files = t.getnames()
        return self.files

    def verify(self, password=None):
        try:
            t = tarfile.open(self.filename, errorlevel=1)

        except tarfile.CompressionError as e:
            raise CRCError(e)

        except (OSError, tarfile.TarError) as e:
            raise ArchiveError(e)

        else:
            t.close()

    def extract(self, password=None):
        self.verify(password)

        try:
            with tarfile.open(self.filename, errorlevel=2) as t:
                
                import os
                
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(t, self.dest)
                self.files = t.getnames()
            return self.files

        except tarfile.ExtractError as e:
            self.log_warning(e)

        except tarfile.CompressionError as e:
            raise CRCError(e)

        except (OSError, tarfile.TarError) as e:
            raise ArchiveError(e)
