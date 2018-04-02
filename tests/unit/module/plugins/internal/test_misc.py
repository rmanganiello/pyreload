# coding=utf-8

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import mock

from module.plugins.internal.misc import DB
from tests.unit.base import BaseUnitTestCase


class TestDb(BaseUnitTestCase):

    def setUp(self):
        super(TestDb, self).setUp()

        self.del_storage_mock = mock.MagicMock()
        self.get_storage_mock = mock.MagicMock()
        self.set_storage_mock = mock.MagicMock()
        self.plugin_mock = mock.MagicMock()
        self.plugin_mock.classname = 'BasePlugin'

        self.plugin_mock.pyload.db.delStorage = self.del_storage_mock
        self.plugin_mock.pyload.db.getStorage = self.get_storage_mock
        self.plugin_mock.pyload.db.setStorage = self.set_storage_mock

        self.db = DB(self.plugin_mock)

    def test_db_store(self):
        self.db.store('tést_key', '{"name": "test"}')
        self.assertEqual(1, self.set_storage_mock.call_count)

        self.set_storage_mock.assert_called_once_with(
            'BasePlugin',
            't\xe9st_key',
            b'IntcIm5hbWVcIjogXCJ0ZXN0XCJ9Ig==',
        )

    def test_db_store_object(self):
        self.db.store('tést_key', {"name": "test"})
        self.assertEqual(1, self.set_storage_mock.call_count)

        self.set_storage_mock.assert_called_once_with(
            'BasePlugin',
            't\xe9st_key',
            b'eyJuYW1lIjogInRlc3QifQ==',
        )

    def test_db_store_with_bytestring(self):
        self.db.store(b'test_key', b'{"name": "test"}')
        self.assertEqual(1, self.set_storage_mock.call_count)

        self.set_storage_mock.assert_called_once_with(
            'BasePlugin',
            b'test_key',
            b'IntcIm5hbWVcIjogXCJ0ZXN0XCJ9Ig==',
        )

    def test_db_retrieve(self):
        default_value = 'DEFAULT'

        scenario_dicts = (
            {
                'key': None,
                'entry': None,
                'expected': default_value,
            },
            {
                'key': 'tést',
                'entry': None,
                'expected': default_value,
            },
            {
                'key': 'tést',
                'entry': b'IntcIm5hbWVcIjogXCJ0ZXN0XCJ9Ig==',
                'expected': '{"name": "test"}',
            },
            {
                'key': None,
                'entry': {
                    'test': b'IntcIm5hbWVcIjogXCJ0ZXN0XCJ9Ig==',
                    'test2': b'IntcIm5hbWVcIjogXCJ0ZXN0XCIsIFwiYWdlXCI6IDMwfSI=',
                },
                'expected': {
                    'test': '{"name": "test"}',
                    'test2': '{"name": "test", "age": 30}',
                },
            },
        )

        for scenario in scenario_dicts:
            self.get_storage_mock.return_value = scenario['entry']

            self.assertEqual(
                self.db.retrieve(scenario['key'], default_value),
                scenario['expected'],
            )
