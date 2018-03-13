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
