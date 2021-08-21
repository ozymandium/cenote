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

    def test_wrong_units(self):
        bad_time = {
            "time": "60in^3",
            "depth": "12in",
        }
        bad_depth = {
            "time": "60s",
            "depth": "2kPa",
        }
        self.assertRaises(pint.errors.DimensionalityError, gu.DepthProfilePoint.from_dict, bad_time)
        self.assertRaises(pint.errors.DimensionalityError, gu.DepthProfilePoint.from_dict, bad_depth)


class TestDepthProfileSection(PintAlmostEqual):

    def test_construction(self):
        pt0 = gu.DepthProfilePoint(1*UREG.minute, depth=12*UREG.foot)
        pt1 = gu.DepthProfilePoint(2*UREG.minute, depth=15*UREG.foot)
        section = gu.DepthProfileSection(pt0, pt1)
        self.assertEqual(section.avg_depth, 13.5*UREG.foot)
        self.assertEqual(section.duration, 60*UREG.second)


    def test_surface_gas_usage(self):
        pt0 = gu.DepthProfilePoint(0*UREG.minute, depth=0*UREG.foot)
        pt1 = gu.DepthProfilePoint(1*UREG.minute, depth=0*UREG.foot)

    def test_depth_gas_usage_square(self):
        pass

    def test_trapezoid_gas_usage(self):
        pass


if __name__ == "__main__":
    unittest.main()
