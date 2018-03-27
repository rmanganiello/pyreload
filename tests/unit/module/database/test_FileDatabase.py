# coding=utf-8

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import mock
import six

from module.database.DatabaseBackend import DatabaseBackend
from module.database.FileDatabase import FileMethods
from tests.unit.base import BaseUnitTestCase


class TestFileMethods(BaseUnitTestCase):

    def setUp(self):
        super(TestFileMethods, self).setUp()

        DatabaseBackend.registerSub(FileMethods)

        self.db = DatabaseBackend(None)
        self.db.setup()

    def tearDown(self):
        self.db.purgeLinks()
        self.db.shutdown()
        super(TestFileMethods, self).tearDown()

    def _create_package(self, **kwargs):
        package_order = kwargs.get('order', 20)

        with mock.patch.object(FileMethods, '_nextPackageOrder', return_value=package_order):
            package_id = self.db.addPackage(
                name=kwargs.get('name', '¯\_(ツ)_/¯'),
                folder=kwargs.get('folder', '/home/user/Downloads/'),
                queue=kwargs.get('queue', 70),
            )

        return package_id

    def test_create_and_retrieve_link(self):
        package_id = self._create_package()

        with mock.patch.object(FileMethods, '_nextFileOrder', return_value=10):
            link_id = self.db.addLink(
                url='https://www.example.org/download_link?attr=1',
                name='Examplé download link',
                plugin='ExamplePlugin',
                package=package_id,
            )

        link = self.db.getLinkData(link_id)

        self.assertDictEqual(
            link,
            {
                link_id: {
                    'id': link_id,
                    'url': 'https://www.example.org/download_link?attr=1',
                    'name': 'Examplé download link',
                    'size': 0,
                    'format_size': '0.00 B',
                    'status': 3,
                    'statusmsg': 'queued',
                    'error': '',
                    'plugin': 'ExamplePlugin',
                    'package': package_id,
                    'order': 10,
                },
            }
        )

        unicode_keys = ('url', 'name', 'format_size', 'statusmsg', 'error', 'plugin')
        for key in unicode_keys:
            self.assertIsInstance(link[link_id][key], six.text_type)

    def test_create_and_retrieve_link_with_bytestring(self):
        package_id = self._create_package()

        with mock.patch.object(FileMethods, '_nextFileOrder', return_value=10):
            link_id = self.db.addLink(
                url=b'https://www.example.org/download_link?attr=1',
                name=b'Example download link',
                plugin=b'ExamplePlugin',
                package=package_id,
            )

        link = self.db.getLinkData(link_id)

        self.assertDictEqual(
            link,
            {
                link_id: {
                    'id': link_id,
                    'url': 'https://www.example.org/download_link?attr=1',
                    'name': 'Example download link',
                    'size': 0,
                    'format_size': '0.00 B',
                    'status': 3,
                    'statusmsg': 'queued',
                    'error': '',
                    'plugin': 'ExamplePlugin',
                    'package': package_id,
                    'order': 10,
                },
            }
        )

        unicode_keys = ('url', 'name', 'format_size', 'statusmsg', 'error', 'plugin')
        for key in unicode_keys:
            self.assertIsInstance(link[link_id][key], six.text_type)

    def test_create_and_retrieve_links_in_batch(self):
        links = [
            {
                'order': 10,
                'url': 'https://www.example.org/download_link?attr=1',
                'plugin': 'ExamplePlugin',
            },
            {
                'order': 11,
                'url': 'https://www.example.org/download_link?attr=2',
                'plugin': 'ExamplePlugin',
            },
            {
                'order': 12,
                'url': 'https://www.example.org/download_link?attr=3',
                'plugin': 'ExamplePlugin',
            },
        ]

        package_id = self._create_package()

        with mock.patch.object(FileMethods, '_nextFileOrder', return_value=10):
            self.db.addLinks(
                links=[
                    (
                        link['url'],
                        link['plugin'],
                    )
                    for link in links
                ],
                package=package_id,
            )

        for index, link in enumerate(links):
            link_id = index + 1
            link_information = self.db.getLinkData(link_id)

            self.assertDictEqual(
                link_information,
                {
                    link_id: {
                        'id': link_id,
                        'url': link['url'],
                        'name': link['url'],
                        'size': 0,
                        'format_size': '0.00 B',
                        'status': 3,
                        'statusmsg': 'queued',
                        'error': '',
                        'plugin': link['plugin'],
                        'package': package_id,
                        'order': link['order'],
                    },
                }
            )

            unicode_keys = ('url', 'name', 'format_size', 'statusmsg', 'error', 'plugin')
            for key in unicode_keys:
                self.assertIsInstance(link_information[link_id][key], six.text_type)
