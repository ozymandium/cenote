from scuba import gas_usage as gu
import unittest
import pint


UREG = gu.UREG


class PintAlmostEqual(unittest.TestCase):

    def assertPintAlmostEqual(self, val0, val1, tol):
        diff = abs(val0 - val1)
        self.assertLess(diff, tol)


class TestPressureAtDepth(PintAlmostEqual):

    def test_exact(self):
        VALUES = {
            0 * UREG.ft: 1 * UREG.atm,
            33 * UREG.ft: 2 * UREG.atm,
            66 * UREG.ft: 3 * UREG.atm,
        }

        for depth, pressure in VALUES.items():
            self.assertEqual(gu.pressure_at_depth(depth), pressure)

    def test_almost(self):
        VALUES = {
            10.06 * UREG.m: 2 * UREG.atm,
        }
        PRESSURE_TOLERANCE = 1e-3 * UREG.atm

        for depth, pressure in VALUES.items():
            self.assertPintAlmostEqual(gu.pressure_at_depth(depth), pressure, PRESSURE_TOLERANCE)




if __name__ == "__main__":
    unittest.main()
