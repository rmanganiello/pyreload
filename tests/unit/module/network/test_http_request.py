from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import unittest
from mock import (
    Mock,
    patch,
)

import pycurl
import six
from six.moves.urllib.parse import urlencode

from module.network.CookieJar import CookieJar
from module.network.HTTPRequest import (
    BadHeader,
    HTTPRequest,
    myurlencode,
)
from module.plugins.Plugin import Abort


class HTTPRequestCurlOptionsTestCase(unittest.TestCase):

    def setUp(self):
        pycurl_patcher = patch('module.network.HTTPRequest.pycurl.Curl')
        self.addCleanup(pycurl_patcher.stop)
        pycurl_patcher.start()
        self.curl_options = {
            'interface': 'eth0',
            'proxies': {
                'type': 'socks4',
                'address': '10.0.0.1',
                'port': 8080,
                'username': 'some-user',
                'password': 'some-password',
            },
            'ipv6': False,
        }

        self.expected_pycurl_options = {
            pycurl.FOLLOWLOCATION: 1,
            pycurl.MAXREDIRS: 5,
            pycurl.CONNECTTIMEOUT: 30,
            pycurl.NOSIGNAL: 1,
            pycurl.NOPROGRESS: 1,
            pycurl.AUTOREFERER: 1,
            pycurl.SSL_VERIFYPEER: 0,
            pycurl.LOW_SPEED_TIME: 30,
            pycurl.LOW_SPEED_LIMIT: 5,
            pycurl.USERAGENT: "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0",
            pycurl.HTTPHEADER: [
                "Accept: */*",
                "Accept-Language: en-US,en",
                "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                "Connection: keep-alive",
                "Keep-Alive: 300",
                "Expect:",
            ],
            pycurl.ENCODING: 'gzip, deflate',
            pycurl.PROXYPORT: self.curl_options['proxies']['port'],
            pycurl.PROXY: self.curl_options['proxies']['address'],
            pycurl.INTERFACE: self.curl_options['interface'],
            pycurl.PROXYUSERPWD: "{0}:{1}".format(
                self.curl_options['proxies']['username'],
                self.curl_options['proxies']['password'],
            ),
            pycurl.IPRESOLVE: pycurl.IPRESOLVE_V4,
        }

    def _assert_curl_options(self):
        http_request = HTTPRequest(options=self.curl_options)
        self.expected_pycurl_options.update({
            pycurl.WRITEFUNCTION: http_request.write,
            pycurl.HEADERFUNCTION: http_request.writeHeader,
        })

        for curl_option, value in six.iteritems(self.expected_pycurl_options):
            http_request.c.setopt.assert_any_call(curl_option, value)

    def test_set_interface_socks5(self):
        self.curl_options['proxies']['type'] = 'socks5'
        self.expected_pycurl_options.update({
            pycurl.PROXYTYPE: pycurl.PROXYTYPE_SOCKS5,
        })

        self._assert_curl_options()

    def test_set_interface_http(self):
        self.curl_options['proxies']['type'] = 'http'
        self.expected_pycurl_options.update({
            pycurl.PROXYTYPE: pycurl.PROXYTYPE_HTTP,
        })

        self._assert_curl_options()

    def test_set_interface_username(self):
        self.curl_options['proxies']['type'] = 'http'
        self.expected_pycurl_options.update({
            pycurl.PROXYTYPE: pycurl.PROXYTYPE_HTTP,
        })

        self._assert_curl_options()

    def test_set_interface_ipv6(self):
        self.curl_options['ipv6'] = True
        self.expected_pycurl_options.update({
            pycurl.IPRESOLVE: pycurl.IPRESOLVE_WHATEVER,
        })

        self._assert_curl_options()

    def test_set_interface_auth(self):
        self.curl_options['auth'] = 'auth'
        self.expected_pycurl_options.update({
            pycurl.USERPWD: self.curl_options['auth'],
        })

        self._assert_curl_options()

    def test_set_interface_timeout(self):
        self.curl_options['timeout'] = 10000
        self.expected_pycurl_options.update({
            pycurl.LOW_SPEED_TIME: self.curl_options['timeout'],
        })

        self._assert_curl_options()


class HTTPRequestTestCase(unittest.TestCase):

    def setUp(self):
        pycurl_patcher = patch('module.network.HTTPRequest.pycurl.Curl')
        set_interface_patcher = patch.object(HTTPRequest, 'setInterface')
        self.addCleanup(pycurl_patcher.stop)
        self.addCleanup(set_interface_patcher.stop)
        pycurl_patcher.start()
        set_interface_patcher.start()

        self.cookie_jar_mock = Mock(spec=CookieJar)
        self.http_request = HTTPRequest(cookies=self.cookie_jar_mock)

    def test_default_properties(self):
        self.assertIsNone(self.http_request.rep)
        self.assertEqual(self.http_request.cj, self.cookie_jar_mock)
        self.assertIsNone(self.http_request.lastURL)
        self.assertIsNone(self.http_request.lastEffectiveURL)
        self.assertFalse(self.http_request.abort)
        self.assertEqual(self.http_request.code, 0)
        self.assertEqual(self.http_request.header, "")
        self.assertEqual(self.http_request.headers, [])

    def test_add_cookies(self):
        self.http_request.addCookies()

        self.http_request.c.getinfo.assert_called_with(pycurl.INFO_COOKIELIST)
        self.assertTrue(self.http_request.cj.addCookies.called)

    def test_get_cookies(self):
        mock_cookies = [
            'cookie1',
            'cookie2',
            'cookie3',
        ]
        self.http_request.cj.getCookies.return_value = mock_cookies

        self.http_request.getCookies()

        for cookie in mock_cookies:
            self.http_request.c.setopt.assert_any_call(pycurl.COOKIELIST, cookie)

    def test_clear_cookies(self):
        self.http_request.clearCookies()

        self.http_request.c.setopt.assert_called_with(pycurl.COOKIELIST, "")

    def _assert_set_request_context_default_behavior(self, url):
        self.http_request.c.setopt.assert_any_call(pycurl.URL, url)
        self.assertEqual(self.http_request.c.lastUrl, url)

    def test_set_request_context_post(self):
        expected_url = 'http://www.example.com'
        post_data = {
            'key': 'value',
        }

        self.http_request.setRequestContext(expected_url, {}, post_data, None, None)

        self._assert_set_request_context_default_behavior(expected_url)

        self.http_request.c.setopt.assert_any_call(pycurl.POST, 1)
        self.http_request.c.setopt.assert_any_call(pycurl.POSTFIELDS, myurlencode(post_data))

    def test_set_request_context_post_multipart(self):
        expected_url = 'http://www.example.com'
        post_data = {
            'key': 'value',
        }

        self.http_request.setRequestContext(
            expected_url,
            {},
            post_data,
            None,
            None,
            multipart=True,
        )

        self._assert_set_request_context_default_behavior(expected_url)

        self.http_request.c.setopt.assert_any_call(pycurl.POST, 1)
        self.http_request.c.setopt.assert_any_call(
            pycurl.HTTPPOST,
            [(x, y.encode('utf8')) for x, y in six.iteritems(post_data)]
        )

    def test_set_request_context_get(self):
        url = 'http://www.example.com'
        get_data = {
            'key': 'value',
        }
        expected_url = "{0}?{1}".format(url, urlencode(get_data))

        self.http_request.setRequestContext(
            url,
            get_data,
            {},
            None,
            None,
        )

        self._assert_set_request_context_default_behavior(expected_url)

        self.http_request.c.setopt.assert_any_call(pycurl.POST, 0)

    def test_set_request_context_referer(self):
        expected_url = 'http://www.example.com'
        expected_last_url = 'http://www.lasturl.com'

        self.http_request.lastURL = expected_last_url

        self.http_request.setRequestContext(
            expected_url,
            {},
            {},
            True,
            None,
        )

        self._assert_set_request_context_default_behavior(expected_url)

        self.http_request.c.setopt.assert_any_call(pycurl.POST, 0)
        self.http_request.c.setopt.assert_any_call(pycurl.REFERER, expected_last_url)

    def test_set_request_context_cookies(self):
        expected_url = 'http://www.example.com'
        mock_cookies = [
            'cookie1',
            'cookie2',
            'cookie3',
        ]
        self.http_request.cj.getCookies.return_value = mock_cookies

        self.http_request.setRequestContext(
            expected_url,
            {},
            {},
            None,
            True,
        )

        self._assert_set_request_context_default_behavior(expected_url)

        self.http_request.c.setopt.assert_any_call(pycurl.POST, 0)
        self.http_request.c.setopt.assert_any_call(pycurl.COOKIEFILE, "")
        self.http_request.c.setopt.assert_any_call(pycurl.COOKIEJAR, "")

    @patch.object(HTTPRequest, 'verifyHeader')
    @patch.object(HTTPRequest, 'addCookies')
    @patch.object(HTTPRequest, 'getResponse', return_value='expected_response')
    @patch.object(HTTPRequest, 'setRequestContext')
    def test_load(self, set_request_context_mock, *args):
        self.http_request.rep = Mock()
        close_rep_mock = self.http_request.rep.close
        expected_url = 'http://www.example.com'

        response = self.http_request.load(expected_url)

        self.assertEqual(response, 'expected_response')
        set_request_context_mock.assert_called_with(
            expected_url,
            {},
            {},
            True,
            True,
            False,
        )
        for mock in args:
            self.assertTrue(mock.called)
        self.http_request.c.setopt.assert_any_call(pycurl.HTTPHEADER, self.http_request.headers)
        self.http_request.c.setopt.assert_any_call(pycurl.POSTFIELDS, "")
        self.http_request.c.getinfo.assert_any_call(pycurl.EFFECTIVE_URL)
        self.assertTrue(self.http_request.c.perform.called)
        self.assertTrue(close_rep_mock.called)
        self.assertEqual(self.http_request.header, "")

    @patch.object(HTTPRequest, 'verifyHeader')
    @patch.object(HTTPRequest, 'addCookies')
    @patch.object(HTTPRequest, 'setRequestContext')
    def test_load_just_header(self, set_request_context_mock, *args):
        self.http_request.rep = Mock()
        close_rep_mock = self.http_request.rep.close
        expected_url = 'http://www.example.com'

        response = self.http_request.load(expected_url, just_header=True)

        self.assertEqual(response, self.http_request.header)
        set_request_context_mock.assert_called_with(
            expected_url,
            {},
            {},
            True,
            True,
            False,
        )
        for mock in args:
            self.assertTrue(mock.called)
        self.http_request.c.setopt.assert_any_call(pycurl.HTTPHEADER, self.http_request.headers)
        self.http_request.c.setopt.assert_any_call(pycurl.POSTFIELDS, "")
        self.http_request.c.setopt.assert_any_call(pycurl.FOLLOWLOCATION, 0)
        self.http_request.c.setopt.assert_any_call(pycurl.FOLLOWLOCATION, 1)
        self.http_request.c.setopt.assert_any_call(pycurl.NOBODY, 1)
        self.http_request.c.setopt.assert_any_call(pycurl.NOBODY, 0)
        self.http_request.c.getinfo.assert_any_call(pycurl.EFFECTIVE_URL)
        self.assertTrue(self.http_request.c.perform.called)
        self.assertTrue(close_rep_mock.called)
        self.assertEqual(self.http_request.header, "")

    @patch.object(HTTPRequest, 'decodeResponse', return_value='expected_response')
    @patch.object(HTTPRequest, 'verifyHeader')
    @patch.object(HTTPRequest, 'addCookies')
    @patch.object(HTTPRequest, 'getResponse')
    @patch.object(HTTPRequest, 'setRequestContext')
    def test_load_decode(self, set_request_context_mock, *args):
        self.http_request.rep = Mock()
        close_rep_mock = self.http_request.rep.close
        expected_url = 'http://www.example.com'

        response = self.http_request.load(expected_url, decode=True)

        self.assertEqual(response, 'expected_response')
        set_request_context_mock.assert_called_with(
            expected_url,
            {},
            {},
            True,
            True,
            False,
        )
        for mock in args:
            self.assertTrue(mock.called)
        self.http_request.c.setopt.assert_any_call(pycurl.HTTPHEADER, self.http_request.headers)
        self.http_request.c.setopt.assert_any_call(pycurl.POSTFIELDS, "")
        self.http_request.c.getinfo.assert_any_call(pycurl.EFFECTIVE_URL)
        self.assertTrue(self.http_request.c.perform.called)
        self.assertTrue(close_rep_mock.called)
        self.assertEqual(self.http_request.header, "")

    def test_get_response(self):
        response = self.http_request.getResponse()

        self.assertEqual(response, "")

        self.http_request.rep = Mock()
        response = self.http_request.getResponse()
        self.assertTrue(self.http_request.rep.getvalue.called)

    @patch.object(HTTPRequest, 'getResponse')
    @patch('module.network.HTTPRequest.open')
    def test_write_exceeded_limit(self, open_mock, get_response_mock):
        expected_text = 'some-text'
        expected_response = 'expected_response'
        get_response_mock.return_value = expected_response

        self.http_request.rep = Mock()
        self.http_request.rep.tell.return_value = 2000000
        with self.assertRaises(Exception):
            self.http_request.write(expected_text)
            self.assertTrue(self.http_request.getResponse.called)
            open_mock.assert_called_once_with('response.dump', 'wb')
            open_mock.write.assert_called_once_with(expected_response)
            self.assertTrue(open_mock.close.called)
            self.assertFalse(self.http_request.write.called)

    @patch.object(HTTPRequest, 'getResponse')
    def test_write_abort(self, get_response_mock):
        expected_text = 'some-text'
        expected_response = 'expected_response'
        get_response_mock.return_value = expected_response

        self.http_request.abort = True
        self.http_request.rep = Mock()
        self.http_request.rep.tell.return_value = 2000000
        with self.assertRaises(Abort):
            self.http_request.write(expected_text)
            self.assertTrue(self.http_request.getResponse.called)

    def test_write(self):
        expected_text = 'some-text'
        self.http_request.rep = Mock()
        self.http_request.rep.tell.return_value = 50000

        self.http_request.write(expected_text)

        self.http_request.rep.write.assert_called_once_with(expected_text)

    def test_write_header(self):
        expected_text = 'some-text'
        self.http_request.writeHeader(expected_text)

        self.assertEqual(self.http_request.header, expected_text)

    def test_put_header(self):
        expected_name = 'some-name'
        expected_value = 'some-value'

        self.http_request.putHeader(expected_name, expected_value)

        self.assertIn(
            '{0}: {1}'.format(expected_name, expected_value),
            self.http_request.headers
        )

    @patch.object(HTTPRequest, 'getResponse', return_value='')
    def test_verify_header_with_bad_header(self, get_response_mock):
        self.http_request.c.getinfo.return_value = '400'

        with self.assertRaises(BadHeader):
            self.http_request.verifyHeader()
            self.assertTrue(get_response_mock.called)
            self.http_request.c.getinfo.assert_any_call(pycurl.RESPONSE_CODE)

    def test_verify_header_without_bad_header(self):
        expected_code = '200'
        self.http_request.c.getinfo.return_value = expected_code

        code = self.http_request.verifyHeader()
        self.http_request.c.getinfo.assert_any_call(pycurl.RESPONSE_CODE)

        self.assertEqual(code, int(expected_code))

    def test_check_header_in_bad_headers(self):
        bad_header = '400'
        self.http_request.c.getinfo.return_value = bad_header

        is_good_header = self.http_request.checkHeader()

        self.http_request.c.getinfo.assert_any_call(pycurl.RESPONSE_CODE)
        self.assertFalse(is_good_header)

    def test_check_header_not_in_bad_headers(self):
        bad_header = '200'
        self.http_request.c.getinfo.return_value = bad_header

        is_good_header = self.http_request.checkHeader()

        self.http_request.c.getinfo.assert_any_call(pycurl.RESPONSE_CODE)
        self.assertTrue(is_good_header)

    def test_clear_headers(self):
        self.http_request.headers = ['some-value', 'another-value']

        self.http_request.clearHeaders()

        self.assertEqual(self.http_request.headers, [])

    def test_close(self):
        self.http_request.rep = Mock()
        rep_close_mock = self.http_request.rep.close
        self.http_request.c = Mock()
        c_close_mock = self.http_request.c.close
        self.http_request.cj = Mock()

        self.http_request.close()

        self.assertTrue(rep_close_mock.called)
        self.assertTrue(c_close_mock.called)
        self.assertFalse(hasattr(self.http_request, 'rep'))
        self.assertFalse(hasattr(self.http_request, 'cj'))
        self.assertFalse(hasattr(self.http_request, 'c'))
