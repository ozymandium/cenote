from cenote import tank
from cenote import config
import unittest
import pint


UREG = config.UREG


class PintTest(unittest.TestCase):
    """Helper to implement almost equal checking for pint types"""

    def assertPintAlmostEqual(self, val0, val1, tol):
        diff = abs(val0 - val1)
        self.assertLess(diff, tol)

    def assertPintEqual(self, val0, val1):
        val1_eq = val1.to(val0.units)
        self.assertEqual(val0, val1_eq)


class TestTank(PintTest):
    def test_class(self):

        class C80(tank.Tank):
            SERVICE_PRESSURE = 3300 * UREG.psi
            VOLUME = 625 * UREG.inch ** 3

        # https://www.catalinacylinders.com/product/c80/
        # this is an AL80 tank, manufacturer specs don't agree with one another at all.
        # even for the same data sheet
        # so we use a pretty large tolerance
        max_gas_volume = 2265 * UREG.liter

        tolerance = 0.16 * UREG.liter

        self.assertPintAlmostEqual(C80.service_volume(), max_gas_volume, tolerance)
        # self.assertPintEqual(tank.max_gas_volume, max_gas_volume)
        # self.assertPintEqual(max_pressure, tank.max_pressure)
        # self.assertPintAlmostEqual(tank.volume, volume, tolerance)
        # self.assertEqual(tank.max_gas_volume.units, config.VOLUME_UNIT)
        # self.assertEqual(tank.volume.units, config.VOLUME_UNIT)
        # self.assertEqual(tank.max_pressure.units, config.PRESSURE_UNIT)

    # def test_wrong_units(self):
    #     max_gas_volume = 10 * UREG.cm ** 2
    #     max_pressure = 3000 * UREG.psi
    #     self.assertRaises(pint.errors.DimensionalityError, gu.Tank, max_gas_volume, max_pressure)
    #     max_gas_volume = 10 * UREG.liter
    #     max_pressure = 3000 * UREG.foot
    #     self.assertRaises(pint.errors.DimensionalityError, gu.Tank, max_gas_volume, max_pressure)


if __name__ == "__main__":
    unittest.main()
