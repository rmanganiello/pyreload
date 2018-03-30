from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import os

import six

IS_WINDOWS = os.name == 'nt'


def maketrans(frm, to):
    if six.PY2:  # pragma: no cover
        import string
        return string.maketrans(frm, to)

    return bytes.maketrans(frm, to)


def install_translation(translation):
    if six.PY2:  # pragma: no cover
        translation.install(unicode=True)
    else:
        translation.install()
