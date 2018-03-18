# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import unittest

import pytest

from module.common import APIExerciser


@pytest.mark.skip(reason='Broken legacy tests')
class TestApi(unittest.TestCase):

    def __init__(self):
        self.api = APIExerciser.APIExerciser(None, True, "TestUser", "pwhere")

    def test_login(self):
        assert self.api.api.login("crapp", "wrong pw") is False

    def test_random(self):
        for i in range(0, 100):
            self.api.testAPI()
