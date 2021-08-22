from cenote import gas_usage as gu
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


class TestPressureAtDepth(PintTest):
    def test_exact(self):
        VALUES = {
            0 * UREG.ft: 1 * UREG.atm,
            33 * UREG.ft: 2 * UREG.atm,
            66 * UREG.ft: 3 * UREG.atm,
        }

        for depth, pressure in VALUES.items():
            self.assertPintEqual(gu.pressure_at_depth(depth), pressure)

    def test_almost(self):
        VALUES = {
            10.06 * UREG.m: 2 * UREG.atm,
        }
        PRESSURE_TOLERANCE = 1e-3 * UREG.atm

        for depth, pressure in VALUES.items():
            self.assertPintAlmostEqual(gu.pressure_at_depth(depth), pressure, PRESSURE_TOLERANCE)


class TestProfilePoint(PintTest):
    def test_construction(self):
        time = 0.0 * UREG.second
        depth = 0.0 * UREG.meter
        point = gu.ProfilePoint(time, depth)
        self.assertPintEqual(time, point.time)
        self.assertEqual(point.time.units, config.TIME_UNIT)
        self.assertPintEqual(depth, point.depth)
        self.assertEqual(point.depth.units, config.DEPTH_UNIT)

    def test_wrong_units(self):
        good_time = 0.0 * UREG.second
        bad_time = UREG.parse_expression("60in^3")
        good_depth = UREG.parse_expression("12in")
        bad_depth = UREG.parse_expression("2kPa")
        self.assertRaises(pint.errors.DimensionalityError, gu.ProfilePoint, bad_time, good_depth)
        self.assertRaises(pint.errors.DimensionalityError, gu.ProfilePoint, good_time, bad_depth)

    def test_negative_value(self):
        self.assertRaises(ValueError, gu.ProfilePoint, -1 * UREG.minute, 0 * UREG.meter)
        self.assertRaises(ValueError, gu.ProfilePoint, 0 * UREG.minute, -1 * UREG.meter)


class TestProfileSection(PintTest):

    # we define stuff in liters and the moduel does stuff in ft^3 (maybe, who knows, it's configurable)
    # so give it a little numerical round off wiggle room.
    GAS_USAGE_VOLUME_TOLERANCE = 1e-12 * config.VOLUME_UNIT

    def test_construction(self):
        pt0 = gu.ProfilePoint(1 * UREG.minute, depth=12 * UREG.foot)
        pt1 = gu.ProfilePoint(2 * UREG.minute, depth=15 * UREG.foot)
        section = gu.ProfileSection(pt0, pt1)
        self.assertPintEqual(section.avg_depth, 13.5 * UREG.foot)
        self.assertPintEqual(section.duration, 60 * UREG.second)

    def test_surface_gas_usage(self):
        pt0 = gu.ProfilePoint(0 * UREG.minute, depth=0 * UREG.foot)
        pt1 = gu.ProfilePoint(2.5 * UREG.minute, depth=0 * UREG.foot)
        scr = gu.Scr(UREG.parse_expression("1.5 l/min"))
        section = gu.ProfileSection(pt0, pt1)
        consumption = section.gas_usage(scr)
        self.assertPintAlmostEqual(consumption, 3.75 * UREG.liter, self.GAS_USAGE_VOLUME_TOLERANCE)

    def test_depth_gas_usage_square(self):
        pt0 = gu.ProfilePoint(0 * UREG.minute, depth=66 * UREG.foot)
        pt1 = gu.ProfilePoint(2.5 * UREG.minute, depth=66 * UREG.foot)
        scr = gu.Scr(UREG.parse_expression("1.5 l/min"))
        section = gu.ProfileSection(pt0, pt1)
        consumption = section.gas_usage(scr)
        self.assertPintAlmostEqual(
            consumption, 3 * 3.75 * UREG.liter, self.GAS_USAGE_VOLUME_TOLERANCE
        )

    def test_trapezoid_gas_usage(self):
        pt0 = gu.ProfilePoint(0 * UREG.minute, depth=0 * UREG.foot)
        pt1 = gu.ProfilePoint(2.5 * UREG.minute, depth=66 * UREG.foot)
        scr = gu.Scr(UREG.parse_expression("1.5 l/min"))
        section = gu.ProfileSection(pt0, pt1)
        consumption = section.gas_usage(scr)
        self.assertPintAlmostEqual(
            consumption, 2 * 3.75 * UREG.liter, self.GAS_USAGE_VOLUME_TOLERANCE
        )


class TestTank(PintTest):
    def test_construction(self):
        # https://www.catalinacylinders.com/product/c80/
        # this is an AL80 tank, manufacturer specs don't agree with one another at all.
        # even for the same data sheet
        # so we use a pretty large tolerance
        max_gas_volume = 2265 * UREG.liter
        max_pressure = 3300 * UREG.psi
        volume = 625 * UREG.inch ** 3
        tolerance = 0.16 * UREG.liter
        tank = gu.Tank(max_gas_volume, max_pressure)
        self.assertPintEqual(tank.max_gas_volume, max_gas_volume)
        self.assertPintEqual(max_pressure, tank.max_pressure)
        self.assertPintAlmostEqual(tank.volume, volume, tolerance)
        self.assertEqual(tank.max_gas_volume.units, config.VOLUME_UNIT)
        self.assertEqual(tank.volume.units, config.VOLUME_UNIT)
        self.assertEqual(tank.max_pressure.units, config.PRESSURE_UNIT)

    def test_wrong_units(self):
        max_gas_volume = 10 * UREG.cm ** 2
        max_pressure = 3000 * UREG.psi
        self.assertRaises(pint.errors.DimensionalityError, gu.Tank, max_gas_volume, max_pressure)
        max_gas_volume = 10 * UREG.liter
        max_pressure = 3000 * UREG.foot
        self.assertRaises(pint.errors.DimensionalityError, gu.Tank, max_gas_volume, max_pressure)


class TestSac(PintTest):
    def test_construction(self):
        pressure_rate = 1 * UREG.psi / UREG.minute
        max_gas_volume = 100 * UREG.liter
        max_pressure = 100 * UREG.psi
        tank = gu.Tank(max_gas_volume, max_pressure)
        sac = gu.Sac(pressure_rate, tank)
        self.assertPintEqual(sac.pressure_rate, pressure_rate)
        self.assertPintEqual(sac.tank.max_gas_volume, max_gas_volume)
        self.assertPintEqual(sac.tank.max_pressure, max_pressure)

    def test_construction_wrong_units(self):
        pressure_rate = 1 * UREG.psi / UREG.gram
        max_gas_volume = 100 * UREG.liter
        max_pressure = 100 * UREG.psi
        tank = gu.Tank(max_gas_volume, max_pressure)
        self.assertRaises(pint.errors.DimensionalityError, gu.Sac, pressure_rate, tank)

    def test_scr(self):
        pressure_rate = UREG.parse_expression("30psi/min")
        max_gas_volume = 3000 * UREG.liter
        max_pressure = max_pressure = 3000 * UREG.psi
        tank = gu.Tank(max_gas_volume, max_pressure)
        sac = gu.Sac(pressure_rate, tank)
        self.assertPintEqual(sac.scr.volume_rate, 30 * UREG.liter / UREG.minute)


class TestScr(PintTest):
    def test_construction(self):
        volume_rate = 0.1 * UREG.parse_expression("L/min")
        scr = gu.Scr(volume_rate)
        self.assertPintEqual(scr.volume_rate, volume_rate)

    def test_construction_wrong_units(self):
        self.assertRaises(
            pint.errors.DimensionalityError,
            gu.Scr,
            50 * UREG.parse_expression("psi / min"),
        )

    def test_sac(self):
        volume_rate = 1 * UREG.liter / UREG.minute
        max_gas_volume = 100 * UREG.liter
        max_pressure = 100 * UREG.psi
        tank = gu.Tank(max_gas_volume, max_pressure)
        scr = gu.Scr(volume_rate)
        sac = scr.sac(tank)
        self.assertPintEqual(sac.pressure_rate, 1 * UREG.psi / UREG.minute)
        self.assertPintEqual(sac.tank.max_gas_volume, max_gas_volume)
        self.assertPintEqual(sac.tank.max_pressure, max_pressure)

    def test_at_depth(self):
        volume_rate = 1 * UREG.L / UREG.min
        tolerance = volume_rate * 1e-12
        scr = gu.Scr(volume_rate)
        self.assertPintAlmostEqual(scr.at_depth(0 * UREG.ft), volume_rate, tolerance)
        self.assertPintAlmostEqual(scr.at_depth(33 * UREG.ft), 2 * volume_rate, tolerance)
        self.assertPintAlmostEqual(scr.at_depth(66 * UREG.ft), 3 * volume_rate, tolerance)


class TestSacScrRoundTrip(PintTest):
    def test_round_trip(self):
        pressure_rate = 30 * UREG.psi / UREG.minute
        max_gas_volume = 80 * UREG.ft ** 3
        max_pressure = 3000 * UREG.psi
        tank = gu.Tank(max_gas_volume, max_pressure)
        sac = gu.Sac(pressure_rate, tank)
        # leave out the unit conversion here to ensure that units are the same.
        self.assertEqual(sac.scr.volume_rate, sac.scr.sac(tank).scr.volume_rate)


class TestProfile(PintTest):
    def test_construction(self):
        pt0 = gu.ProfilePoint(0 * UREG.minute, depth=0 * UREG.foot)
        pt1 = gu.ProfilePoint(2.5 * UREG.minute, depth=0 * UREG.foot)
        self.assertRaises(AttributeError, gu.Profile, [1, 2])
        self.assertRaises(Exception, gu.Profile, [pt0])
        self.assertRaises(Exception, gu.Profile, [pt1, pt0])
        profile = gu.Profile([pt0, pt1])
        self.assertEqual(pt0.time, profile.points[0].time)
        self.assertEqual(pt0.depth, profile.points[0].depth)
        self.assertEqual(pt1.time, profile.points[1].time)
        self.assertEqual(pt1.depth, profile.points[1].depth)

    def test_nonzero_first_point(self):
        points = [
            gu.ProfilePoint(UREG.parse_expression("1sec"), UREG.parse_expression("1meter")),
            gu.ProfilePoint(UREG.parse_expression("2sec"), UREG.parse_expression("2meter")),
        ]
        self.assertRaises(Exception, gu.Profile, points)


class TestDive(PintTest):
    def test_gas_usage(self):
        points = [
            gu.ProfilePoint(UREG.parse_expression("0 min"), UREG.parse_expression("0 feet")),
            gu.ProfilePoint(UREG.parse_expression("1 min"), UREG.parse_expression("0 feet")),
            gu.ProfilePoint(UREG.parse_expression("2 min"), UREG.parse_expression("66 feet")),
        ]
        profile = gu.Profile(points)
        scr = gu.Scr(1.0 * UREG.liter / UREG.minute)
        dive = gu.Dive(scr, profile)
        self.assertPintAlmostEqual(dive.gas_usage(), 3.0 * UREG.liter, 1e-12 * config.VOLUME_UNIT)


if __name__ == "__main__":
    unittest.main()
