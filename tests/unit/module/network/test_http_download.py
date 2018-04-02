from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from logging import Logger
from mock import (
    Mock,
    patch,
)

import pycurl

from module.network.HTTPChunk import HTTPChunk
from module.network.HTTPDownload import HTTPDownload
from tests.unit.base import BaseUnitTestCase


class HTTPDownloadBaseTestCase(BaseUnitTestCase):
    def setUp(self):
        super(HTTPDownloadBaseTestCase, self).setUp()
        http_chunk_patcher = patch('module.network.HTTPDownload.HTTPChunk', autospec=True)
        chunk_info_patcher = patch('module.network.HTTPDownload.ChunkInfo', autospec=True)
        pycurl_multi_patcher = patch('module.network.HTTPDownload.pycurl.CurlMulti', autospec=True)
        self.addCleanup(http_chunk_patcher.stop)
        self.addCleanup(chunk_info_patcher.stop)
        self.addCleanup(pycurl_multi_patcher.stop)
        self.http_chunk_mock = http_chunk_patcher.start()
        self.chunk_info_mock = chunk_info_patcher.start()
        self.pycurl_multi_mock = pycurl_multi_patcher.start()

        self.chunk_mock_size = 10000
        self.url = 'http://www.example.com'
        self.filename = 'example.file'

    def _chunk_load_mock(self, name):
        self.chunk_info_mock.size = self.chunk_mock_size
        return self.chunk_info_mock


class HTTPDownloadInitializerTestCase(HTTPDownloadBaseTestCase):

    def _assert_default_properties(self, http_download, **kwargs):
        self.assertEqual(http_download.url, self.url)
        self.assertEqual(http_download.filename, self.filename)
        self.assertEqual(http_download.get, kwargs.get('get', {}))
        self.assertEqual(http_download.post, kwargs.get('post', {}))
        self.assertEqual(http_download.options, kwargs.get('options', {}))
        self.assertEqual(http_download.referer, kwargs.get('referer', None))
        self.assertEqual(http_download.cj, kwargs.get('cj', None))
        self.assertEqual(http_download.bucket, kwargs.get('bucket', None))
        self.assertEqual(http_download.disposition, kwargs.get('disposition', False))
        self.assertEqual(http_download.progressNotify, kwargs.get('progressNotify', None))
        self.assertFalse(http_download.abort)
        self.assertIsNone(http_download.nameDisposition)
        self.assertEqual(http_download.chunks, [])
        self.assertIsInstance(http_download.log, Logger)
        self.assertIsNone(http_download.chunkSupport)
        self.assertEqual(http_download.lastArrived, [])
        self.assertEqual(http_download.speeds, [])
        self.assertEqual(http_download.lastSpeeds, [0, 0])

    def test_default_properties(self):
        self.chunk_info_mock.load.side_effect = IOError()
        http_download = HTTPDownload(self.url, self.filename)

        self._assert_default_properties(http_download)
        self.assertFalse(hasattr(http_download, 'infoSaved'))
        self.assertEqual(http_download.size, 0)
        self.chunk_info_mock.assert_called_once_with(self.filename)

    def test_default_resume_properties(self):
        self.chunk_info_mock.load.side_effect = self._chunk_load_mock
        http_download = HTTPDownload(self.url, self.filename)

        self._assert_default_properties(http_download)
        self.assertEqual(http_download.size, self.chunk_mock_size)
        self.assertTrue(http_download.info.resume)
        self.assertTrue(http_download.infoSaved)
        self.chunk_info_mock.load.assert_called_once_with(self.filename)

    def test_init_with_custom_properties(self):
        self.chunk_info_mock.load.side_effect = IOError()
        custom_properties = {
            'get': {'key': 'value'},
            'post': {'key': 'value'},
            'options': {'option1': 'value'},
            'disposition': True,
        }
        http_download = HTTPDownload(
            self.url,
            self.filename,
            **custom_properties
        )

        self._assert_default_properties(http_download, **custom_properties)


class HTTPDownloadTestCase(HTTPDownloadBaseTestCase):

    def setUp(self):
        super(HTTPDownloadTestCase, self).setUp()
        self.chunk_info_mock.load.side_effect = IOError()
        self.http_download = HTTPDownload(self.url, self.filename)

        self.chunk_info_mock.load.side_effect = self._chunk_load_mock
        self.http_download_resumed = HTTPDownload(self.url, self.filename)

    def test_speed(self):
        current_speed = [150.0, 200.0, 120.0]

        self.http_download.speeds = current_speed
        self.http_download.lastSpeeds = [0, 0]  # Default value

        self.assertEqual(self.http_download.speed, sum(current_speed))

        last_speed = [120.0, 110.5, 115.0]

        self.http_download.lastSpeeds = [last_speed, 0]

        self.assertEqual(
            self.http_download.speed,
            (sum(last_speed) + sum(current_speed)) / 2,
        )

        last_speed_2 = [130.0, 119, 120]
        self.http_download.lastSpeeds = [last_speed, last_speed_2]

        self.assertEqual(
            self.http_download.speed,
            (sum(last_speed) + sum(last_speed_2) + sum(current_speed)) / 3,
        )

    def test_arrived(self):
        arrived_values = [200, 500, 100]
        expected_chunks = [
            Mock(spec=HTTPChunk),
            Mock(spec=HTTPChunk),
            Mock(spec=HTTPChunk),
        ]

        for idx, chunk in enumerate(expected_chunks):
            chunk.arrived = arrived_values[idx]

        self.http_download.chunks = expected_chunks

        self.assertEqual(self.http_download.arrived, sum(arrived_values))

    def test_percent_without_size(self):
        self.assertEqual(self.http_download.percent, 0)

    def test_percent_with_size(self):
        arrived_values = [500, 500]
        expected_chunks = [
            Mock(spec=HTTPChunk),
            Mock(spec=HTTPChunk),
        ]

        for idx, chunk in enumerate(expected_chunks):
            chunk.arrived = arrived_values[idx]

        expected_size = 2000
        self.http_download.chunks = expected_chunks
        self.http_download.size = expected_size

        self.assertEqual(
            self.http_download.percent,
            (sum(arrived_values) * 100) / expected_size,
        )

    def test_update_progress(self):
        self.http_download.progressNotify = Mock()

        self.http_download.updateProgress()

        self.http_download.progressNotify.assert_called_once_with(self.http_download.percent)

    def test_close_chunk(self):
        chunk = Mock(spec=HTTPChunk)
        chunk.c = Mock(spec=pycurl.Curl)

        self.http_download.closeChunk(chunk)

        self.assertEqual(chunk.close.call_count, 1)
        self.http_download.m.remove_handle.assert_called_once_with(chunk.c)

    def test_close_chunk_with_pycurl_error(self):
        chunk = Mock(spec=HTTPChunk)
        chunk.c = Mock(spec=pycurl.Curl)
        self.http_download.m.remove_handle.side_effect = pycurl.error

        self.http_download.closeChunk(chunk)

        self.assertEqual(chunk.close.call_count, 1)
        self.http_download.m.remove_handle.assert_called_once_with(chunk.c)

    @patch.object(HTTPDownload, 'closeChunk')
    def test_close(self, close_chunk_mock):
        chunks = [
            Mock(spec=HTTPChunk),
            Mock(spec=HTTPChunk),
            Mock(spec=HTTPChunk),
        ]
        self.http_download.chunks = chunks
        pycurl_multi_close_mock = self.http_download.m.close

        self.http_download.close()

        for chunk in chunks:
            close_chunk_mock.assert_any_call(chunk)
        self.assertEqual(self.http_download.chunks, [])
        self.assertEqual(pycurl_multi_close_mock.call_count, 1)
        self.assertFalse(hasattr(self.http_download, 'm'))
        self.assertFalse(hasattr(self.http_download, 'cj'))
        self.assertFalse(hasattr(self.http_download, 'info'))
