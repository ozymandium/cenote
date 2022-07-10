from cenote.water import *
from cenote import config
import bungee

import unittest
from pint.testsuite import helpers


UREG = config.UREG


class TestPressureAtDepth(unittest.TestCase):
    """https://bluerobotics.com/learn/pressure-depth-calculator/"""

    def test_almost(self):
        VALUES = {
            bungee.Water.FRESH: {
                100 * UREG.meter: 141.81 * UREG.psi,
                32.81 * UREG.ft: 14.18 * UREG.psi,
            },
            bungee.Water.SALT: {
                100 * UREG.meter: 145.59 * UREG.psi,
                32.81 * UREG.ft: 14.56 * UREG.psi,
            },
        }
        PRESSURE_TOLERANCE = (1e-3 * UREG.atm).to(UREG.psi).magnitude

        for water in VALUES:
            for depth in VALUES[water]:
                expected_water_pressure = VALUES[water][depth]
                expected_pressure = expected_water_pressure + 1 * UREG.atm
                water_pressure = water_pressure_from_depth(depth, water)
                pressure = pressure_from_depth(depth, water)
                helpers.assert_quantity_almost_equal(
                    water_pressure, expected_water_pressure, PRESSURE_TOLERANCE
                )
                helpers.assert_quantity_almost_equal(
                    pressure, expected_pressure, PRESSURE_TOLERANCE
                )
