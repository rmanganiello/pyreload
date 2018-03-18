from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import six


def smart_bytes(value, encoding='utf-8', **kwargs):
    if isinstance(value, six.binary_type):
        return value
    elif isinstance(value, six.text_type):
        return value.encode(encoding=encoding, **kwargs)
    else:
        return six.text_type(value).encode(encoding=encoding, **kwargs)


def smart_text(value, encoding='utf-8', **kwargs):
    if isinstance(value, six.text_type):
        return value
    elif isinstance(value, six.binary_type):
        return value.decode(encoding=encoding, **kwargs)
    else:
        return six.text_type(value)


def smart_str(value, encoding='utf-8', **kwargs):
    """Returns a bytestring on Python 2 and unicode string on Python 3."""
    if six.PY2:
        return smart_bytes(value, encoding, **kwargs)
    return smart_text(value, encoding, **kwargs)
