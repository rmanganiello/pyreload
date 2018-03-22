from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import unittest
from logging import Logger
from mock import patch

from module.network.Browser import Browser


class BrowserTestCase(unittest.TestCase):

    def setUp(self):
        # Patchers
        self.http_request_patcher = patch('module.network.Browser.HTTPRequest')
        self.http_download_patcher = patch('module.network.Browser.HTTPDownload')
        self.cookie_jar_patcher = patch('module.network.CookieJar.CookieJar')
        # Mocks
        self.http_request_mock = self.http_request_patcher.start()
        self.http_download_mock = self.http_download_patcher.start()
        self.cookie_jar_mock = self.cookie_jar_patcher.start()

        self.browser = Browser()

    def tearDown(self):
        self.http_request_patcher.stop()
        self.http_download_patcher.stop()
        self.cookie_jar_patcher.stop()

    def test_default_properties(self):
        self.assertIsInstance(self.browser.log, Logger)
        self.assertIsNone(self.browser.cj)
        self.assertIsNone(self.browser.dl)
        self.assertIsNone(self.browser.bucket)
        self.assertEqual(self.browser._size, 0)
        self.assertEqual(self.browser.speed, 0)
        self.assertEqual(self.browser.size, 0)
        self.assertEqual(self.browser.arrived, 0)
        self.assertEqual(self.browser.percent, 0)
        self.assertEqual(self.browser.code, self.browser.http.code)
        self.assertEqual(self.browser.lastEffectiveURL, self.browser.http.lastEffectiveURL)
        self.http_request_mock.assert_called_with(
            self.browser.cj,
            self.browser.options,
        )

    def test_add_auth(self):
        expected_password = '1234'
        self.browser.addAuth(expected_password)

        self.assertEqual(self.browser.options['auth'], expected_password)
        self.assertTrue(self.browser.http.close.called)

    def test_last_url(self):
        self.assertEqual(self.browser.lastURL, self.browser.http.lastURL)

        expected_url = 'http://anotherurl.com'
        self.browser.lastURL = expected_url

        self.assertEqual(self.browser.http.lastURL, expected_url)

    def test_set_cookie_jar(self):
        cj = self.cookie_jar_mock()
        self.browser.setCookieJar(cj)

        self.assertEqual(self.browser.cj, cj)
        self.assertEqual(self.browser.http.cj, cj)

    def test_size_with_dl(self):
        expected_size = 1024
        dl = self.http_download_mock()
        dl.size = expected_size

        self.browser.dl = dl
        self.assertEqual(self.browser.size, expected_size)

    def test_size_with_inner_size(self):
        expected_size = 1024
        self.browser._size = expected_size

        self.assertEqual(self.browser.size, expected_size)

    def test_arrived(self):
        expected_arrived = 1024
        dl = self.http_download_mock()
        dl.arrived = expected_arrived

        self.browser.dl = dl
        self.assertEqual(self.browser.arrived, expected_arrived)

    def test_percent(self):
        total_size = 1024
        arrived_size = 256

        dl = self.http_download_mock()
        dl.size = total_size
        dl.arrived = arrived_size
        self.browser.dl = dl

        self.assertEqual(self.browser.percent, (arrived_size * 100) / total_size)

    def test_speed(self):
        expected_speed = 100
        dl = self.http_download_mock()
        dl.speed = expected_speed
        self.browser.dl = dl

        self.assertEqual(self.browser.speed, expected_speed)

    def test_clear_cookies(self):
        # Without cj
        self.browser.clearCookies()

        self.assertTrue(self.browser.http.clearCookies.called)

        # With cj
        cj = self.cookie_jar_mock()
        self.browser.cj = cj
        self.browser.clearCookies()

        self.assertTrue(cj.clear.called)
        self.assertTrue(self.browser.http.clearCookies.called)

    def test_clear_referer(self):
        self.browser.clearReferer()

        self.assertIsNone(self.browser.http.lastURL)

    def test_abort_downloads(self):
        expected_size = 1024
        dl = self.http_download_mock()
        dl.size = expected_size
        self.browser.dl = dl

        self.browser.abortDownloads()
        self.assertTrue(self.browser.http.abort)
        self.assertEqual(self.browser.size, expected_size)
        self.assertTrue(self.browser.dl.abort)

    def test_remove_auth(self):
        self.browser.addAuth('1234')
        self.browser.removeAuth()

        self.assertNotIn('auth', self.browser.options)

    def test_set_option(self):
        expected_key = 'some-key'
        expected_value = 'some-value'

        self.browser.setOption(expected_key, expected_value)

        self.assertIn(expected_key, self.browser.options)
        self.assertEqual(self.browser.options[expected_key], expected_value)

    def test_delete_option(self):
        expected_key = 'some-key'
        self.browser.options[expected_key] = 'some-value'
        self.browser.deleteOption(expected_key)

        self.assertNotIn(expected_key, self.browser.options)

    def test_load(self):
        expected_args = ['arg1', 'arg2']
        expected_kwargs = {
            'key1': 'value1',
            'key2': 'value2',
        }
        self.browser.load(expected_args, expected_kwargs)
        self.browser.http.load.assert_called_with(expected_args, expected_kwargs)

    def test_put_header(self):
        expected_header_name = 'header-name'
        expected_value_name = 'value-name'

        self.browser.putHeader(expected_header_name, expected_value_name)

        self.browser.http.putHeader.assert_called_with(expected_header_name, expected_value_name)

    def test_clear_headers(self):
        self.browser.clearHeaders()

        self.assertTrue(self.browser.http.clearHeaders.called)

    def test_close(self):
        self.browser.close()
        self.assertFalse(hasattr(self.browser, 'http'))
        self.assertFalse(hasattr(self.browser, 'dl'))
        self.assertFalse(hasattr(self.browser, 'cj'))

    def test_http_download(self):
        expected_url = 'sampleurl'
        expected_filename = 'filename.file'
        self.browser.httpDownload(expected_url, expected_filename)
        self.http_download_mock.assert_called_with(
            expected_url,
            expected_filename,
            {},
            {},
            self.browser.lastEffectiveURL,
            self.browser.cj,
            self.browser.bucket,
            self.browser.options,
            None,
            False,
        )
        self.assertIsNone(self.browser.dl)
