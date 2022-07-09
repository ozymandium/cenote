from cenote import tank
from cenote import config
from cenote.mix import AIR, EAN50

import unittest
import pint
from pint.testsuite import QuantityTestCase, helpers


UREG = config.UREG


class TestTank(unittest.TestCase, QuantityTestCase):
    def test_service_volumes(self):
        TOLERANCE = 0.05
        helpers.assert_quantity_almost_equal(
            tank.Aluminum13.service_volume(), 13.0 * UREG.ft ** 3, TOLERANCE
        )
        helpers.assert_quantity_almost_equal(
            tank.Aluminum40.service_volume(), 40.0 * UREG.ft ** 3, TOLERANCE
        )
        helpers.assert_quantity_almost_equal(
            tank.Aluminum80.service_volume(), 77.4 * UREG.ft ** 3, TOLERANCE
        )
        helpers.assert_quantity_almost_equal(
            tank.LowPressureSteel108.service_volume(), 107.8 * UREG.ft ** 3, TOLERANCE
        )

    def test_create_full(self):
        self.assertEqual(
            tank.Aluminum80.create_full(AIR).pressure, tank.Aluminum80.SERVICE_PRESSURE
        )

    def test_create_empty(self):
        self.assertEqual(tank.Aluminum80.create_empty(AIR).pressure, 0 * config.PRESSURE_UNIT)

    def test_volume(self):
        self.assertEqual(
            tank.Aluminum80.create_full(AIR).volume(), tank.Aluminum80.service_volume()
        )
        self.assertEqual(tank.Aluminum80.create_empty(AIR).volume(), 0 * config.VOLUME_UNIT)

    def test_pressure_change(self):
        al80 = tank.Aluminum80.create_full(AIR)
        al80.decrease_pressure(al80.SERVICE_PRESSURE / 3.0)
        helpers.assert_quantity_almost_equal(
            al80.pressure, al80.SERVICE_PRESSURE * 2.0 / 3.0, 1e-12
        )

    def test_volume_change(self):
        lp108 = tank.LowPressureSteel108.create_full(EAN50)
        lp108.decrease_volume(lp108.service_volume() / 3.0)
        helpers.assert_quantity_almost_equal(
            lp108.volume(), lp108.service_volume() * 2.0 / 3.0, 1e-12
        )
