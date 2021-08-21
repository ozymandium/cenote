from scuba import gas_usage as gu
import unittest
import pint


UREG = gu.UREG


class PintAlmostEqual(unittest.TestCase):
    """Helper to implement almost equal checking for pint types"""

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


class TestProfilePoint(unittest.TestCase):
    def test_construction(self):
        time = 0.0 * UREG.second
        depth = 0.0 * UREG.foot
        point = gu.ProfilePoint(time, depth)
        self.assertEqual(time, point.time)
        self.assertEqual(depth, point.depth)

    def test_from_dict(self):
        data = {
            "time": "60s",
            "depth": "12in",
        }
        point = gu.ProfilePoint.from_dict(data)
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
        self.assertRaises(pint.errors.DimensionalityError, gu.ProfilePoint.from_dict, bad_time)
        self.assertRaises(
            pint.errors.DimensionalityError, gu.ProfilePoint.from_dict, bad_depth
        )


class TestProfileSection(unittest.TestCase):
    def test_construction(self):
        pt0 = gu.ProfilePoint(1 * UREG.minute, depth=12 * UREG.foot)
        pt1 = gu.ProfilePoint(2 * UREG.minute, depth=15 * UREG.foot)
        section = gu.ProfileSection(pt0, pt1)
        self.assertEqual(section.avg_depth, 13.5 * UREG.foot)
        self.assertEqual(section.duration, 60 * UREG.second)

    def test_surface_gas_usage(self):
        pt0 = gu.ProfilePoint(0 * UREG.minute, depth=0 * UREG.foot)
        pt1 = gu.ProfilePoint(2.5 * UREG.minute, depth=0 * UREG.foot)
        rmv = gu.Rmv(UREG.parse_expression("1.5 l/min"))
        section = gu.ProfileSection(pt0, pt1)
        consumption = section.gas_usage(rmv)
        self.assertEqual(consumption, 3.75 * UREG.liter)

    def test_depth_gas_usage_square(self):
        pt0 = gu.ProfilePoint(0 * UREG.minute, depth=66 * UREG.foot)
        pt1 = gu.ProfilePoint(2.5 * UREG.minute, depth=66 * UREG.foot)
        rmv = gu.Rmv(UREG.parse_expression("1.5 l/min"))
        section = gu.ProfileSection(pt0, pt1)
        consumption = section.gas_usage(rmv)
        self.assertEqual(consumption, 3 * 3.75 * UREG.liter)

    def test_trapezoid_gas_usage(self):
        pt0 = gu.ProfilePoint(0 * UREG.minute, depth=0 * UREG.foot)
        pt1 = gu.ProfilePoint(2.5 * UREG.minute, depth=66 * UREG.foot)
        rmv = gu.Rmv(UREG.parse_expression("1.5 l/min"))
        section = gu.ProfileSection(pt0, pt1)
        consumption = section.gas_usage(rmv)
        self.assertEqual(consumption, 2 * 3.75 * UREG.liter)


class TestTank(unittest.TestCase):
    def test_construction(self):
        volume = 10 * UREG.liter
        max_pressure = 3000 * UREG.psi
        tank = gu.Tank(volume, max_pressure)
        self.assertEqual(volume, tank.volume)
        self.assertEqual(max_pressure, tank.max_pressure)

    def test_wrong_units(self):
        volume = 10 * UREG.cm ** 2
        max_pressure = 3000 * UREG.psi
        self.assertRaises(pint.errors.DimensionalityError, gu.Tank, volume, max_pressure)
        volume = 10 * UREG.liter
        max_pressure = 3000 * UREG.foot
        self.assertRaises(pint.errors.DimensionalityError, gu.Tank, volume, max_pressure)

    def test_from_dict(self):
        data = {
            "volume": "10 liter",
            "max_pressure": "3000 psi",
        }
        tank = gu.Tank.from_dict(data)
        self.assertEqual(tank.volume, 10 * UREG.liter)
        self.assertEqual(tank.max_pressure, 3000 * UREG.psi)


class TestRmv(unittest.TestCase):
    def test_construction(self):
        volume_rate = 0.1 * UREG.parse_expression("L/min")
        rmv = gu.Rmv(volume_rate)
        self.assertEqual(rmv.volume_rate, volume_rate)

    def test_construction_wrong_units(self):
        self.assertRaises(
            pint.errors.DimensionalityError,
            gu.Rmv,
            50 * UREG.parse_expression("psi / min"),
        )

    def test_to_sac(self):
        pass


class TestSac(unittest.TestCase):

    def test_construction(self):
        pass

    def test_construction_wrong_units(self):
        pass

    def test_from_dict_pressure_rate(self):
        data = {
            "pressure_rate": "30psi/min",
            "tank": {
                "volume": "10L",
                "max_pressure": "3000psi",
            }
        }
        sac = gu.Sac.from_dict(data)
        self.assertEqual(sac.pressure_rate, 30 * UREG.psi / UREG.minute)
        self.assertEqual(sac.tank.volume, 10 * UREG.liter)
        self.assertEqual(sac.tank.max_pressure, 3000 * UREG.psi)

    def test_rmv(self):
        pressure_rate = UREG.parse_expression("30psi/min")
        volume=10 * UREG.liter
        max_pressure = max_pressure=3000*UREG.psi
        tank = gu.Tank(volume, max_pressure)
        sac = gu.Sac(pressure_rate, tank)
        self.assertEqual(sac.rmv.volume_rate, 0.1 * UREG.liter / UREG.minute)


class TestSacRmvRoundTrip(unittest.TestCase):
    def test_round_trip(self):
        pass


if __name__ == "__main__":
    unittest.main()
