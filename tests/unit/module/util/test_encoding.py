# coding=utf8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import unittest

import six

from module.util.encoding import (
    smart_bytes,
    smart_text,
)


class TestEncoding(unittest.TestCase):

    def test_smart_bytes(self):
        value_to_expected_tuples = (
            (b'testing', b'testing'),
            (u'testing', b'testing'),
            (b'A\xc3\xb1o', b'A\xc3\xb1o'),
            (u'Año', b'A\xc3\xb1o'),
            (123, b'123'),
            (None, b'None'),
        )

        for value, expected in value_to_expected_tuples:
            result = smart_bytes(value)
            self.assertEqual(result, expected)
            self.assertIsInstance(result, six.binary_type)

    def test_smart_text(self):
        value_to_expected_tuples = (
            (b'testing', u'testing'),
            (u'testing', u'testing'),
            (b'A\xc3\xb1o', u'Año'),
            (u'Año', u'Año'),
            (123, u'123'),
            (None, u'None'),
        )

        for value, expected in value_to_expected_tuples:
            result = smart_text(value)
            self.assertEqual(result, expected)
            self.assertIsInstance(result, six.text_type)
