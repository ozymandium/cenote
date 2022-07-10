from cenote.mix import *
from cenote import config
import bungee

from pint.testsuite import helpers

import unittest


UREG = config.UREG


class TestMix(unittest.TestCase):
    def test_construction(self):
        mix = Mix(0.8)
        self.assertEqual(mix.po2, 0.8)
        helpers.assert_quantity_almost_equal(mix.pn2, 0.2, 1e-12)

    def test_construction_low_o2(self):
        self.assertRaises(ValueError, Mix, 0)
        self.assertRaises(ValueError, Mix, 0.0)
        self.assertRaises(ValueError, Mix, -0.01)

    def test_construction_high_o2(self):
        self.assertEqual(O2.po2, 1)
        self.assertRaises(ValueError, Mix, 1.0001)

    def test_po2_at_depth(self):
        helpers.assert_quantity_almost_equal(
            O2.po2_at_depth(10.094055 * UREG.meter, bungee.Water.SALT), 2.0 * UREG.atm, 1e-6
        )
        helpers.assert_quantity_almost_equal(
            AIR.po2_at_depth(33.9989237 * UREG.foot, bungee.Water.FRESH), 0.418920 * UREG.atm, 1e-6
        )

    def test_mod(self):
        helpers.assert_quantity_almost_equal(AIR.mod(1.4, bungee.Water.SALT), 188 * UREG.foot, 0.5)
        helpers.assert_quantity_almost_equal(O2.mod(1.6, bungee.Water.SALT), 20 * UREG.foot, 0.2)
        helpers.assert_quantity_almost_equal(EAN50.mod(1.6, bungee.Water.SALT), 70 * UREG.foot, 1.0)
