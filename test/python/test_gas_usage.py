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


class TestDepthProfilePoint(PintAlmostEqual):

    def test_from_dict(self):
        data = {
            "time": "60s",
            "depth": "12in",
        }
        point = gu.DepthProfilePoint.from_dict(data)
        self.assertEqual(point.time, 1 * UREG.minute)
        self.assertEqual(point.time.units, UREG.minute)
        self.assertEqual(point.depth, 1 * UREG.foot)
        self.assertEqual(point.depth.units, UREG.foot)


class TestDepthProfileSection(PintAlmostEqual):

    def test_surface(self):
        # pt0 = gu.DepthProfilePoint()
        pass


if __name__ == "__main__":
    unittest.main()
