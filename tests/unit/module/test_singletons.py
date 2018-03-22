from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import mock

from module.singletons import (
    HOOK_MANAGER_SINGLETON,
    REQUEST_FACTORY_SINGLETON,
    SingletonFactory,
)
from tests.unit.base import BaseUnitTestCase


class TestSingletons(BaseUnitTestCase):

    def test_singleton_factory_before_instantiating(self):
        with self.assertRaises(ValueError):
            SingletonFactory.get_instance(REQUEST_FACTORY_SINGLETON)

    def test_singleton_factory_set_and_get(self):
        singleton = mock.MagicMock()

        SingletonFactory.set_instance(REQUEST_FACTORY_SINGLETON, instance=singleton)

        self.assertEqual(
            singleton,
            SingletonFactory.get_instance(REQUEST_FACTORY_SINGLETON),
        )

        # Overwriting works
        singleton2 = mock.MagicMock()

        SingletonFactory.set_instance(REQUEST_FACTORY_SINGLETON, instance=singleton2)

        self.assertEqual(
            singleton2,
            SingletonFactory.get_instance(REQUEST_FACTORY_SINGLETON),
        )

    def test_singleton_factory_with_invalid_singleton(self):
        singleton = mock.MagicMock()

        with self.assertRaises(ValueError):
            SingletonFactory.set_instance('invalid-token', instance=singleton)

    def test_singleton_factory_different_singletons(self):
        singleton = mock.MagicMock()
        singleton2 = mock.MagicMock()

        SingletonFactory.set_instance(HOOK_MANAGER_SINGLETON, instance=singleton)
        SingletonFactory.set_instance(REQUEST_FACTORY_SINGLETON, instance=singleton2)

        self.assertEqual(
            singleton,
            SingletonFactory.get_instance(HOOK_MANAGER_SINGLETON),
        )

        self.assertEqual(
            singleton2,
            SingletonFactory.get_instance(REQUEST_FACTORY_SINGLETON),
        )
