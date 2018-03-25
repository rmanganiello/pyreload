import gettext
import unittest

import six


class BaseUnitTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseUnitTestCase, cls).setUpClass()

        # Install gettext to have _ function in builtins
        # TODO: Remove _ from builtins
        if six.PY2:
            gettext.install(None, unicode=True)
        else:
            gettext.install(None)
