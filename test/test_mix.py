from cenote.mix import *
from cenote import config

from pint.testsuite import helpers

import unittest


UREG = config.UREG


class TestMix(unittest.TestCase):
    def test_construction(self):
        mix = Mix(0.8, 0.1)
        self.assertEqual(mix.po2, 0.8)
        self.assertEqual(mix.phe, 0.1)
        helpers.assert_quantity_almost_equal(mix.pn2, 0.1, 1e-12)
