# coding=utf8

import mock
import unittest

import pyLoadCore


class TestPyLoadCore(unittest.TestCase):

    def setUp(self):
        super(TestPyLoadCore, self).setUp()

        self.core = pyLoadCore.Core()

        patcher_os_exists = mock.patch('os.path.exists')
        patcher_os_makedirs = mock.patch('os.makedirs')

        self.addCleanup(patcher_os_exists.stop)
        self.addCleanup(patcher_os_makedirs.stop)

        self.mock_os_exists = patcher_os_exists.start()
        self.mock_os_makedirs = patcher_os_makedirs.start()

    def test_check_file_with_inexistent_unicode_folder(self):
        self.mock_os_exists.return_value = False

        self.core.check_file(u'parent/folder_name', '', is_folder=True)

        self.mock_os_makedirs.assert_called_once_with(u'parent/folder_name')

    def test_check_file_with_inexistent_unicode_folder_special_chars(self):
        self.mock_os_exists.return_value = False

        self.core.check_file(u'parent/año1/folder_name', '', is_folder=True)

        self.mock_os_makedirs.assert_called_once_with(u'parent/año1/folder_name')

    def test_check_file_with_inexistent_bytestring_folder(self):
        self.mock_os_exists.return_value = False

        self.core.check_file(b'parent/folder_name', '', is_folder=True)

        self.mock_os_makedirs.assert_called_once_with(u'parent/folder_name')

    def test_check_file_with_inexistent_bytestring_folder_special_chars(self):
        self.mock_os_exists.return_value = False

        self.core.check_file(b'parent/a\xc3\xb1o1/folder_name', '', is_folder=True)

        self.mock_os_makedirs.assert_called_once_with(u'parent/año1/folder_name')
