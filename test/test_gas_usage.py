from cenote import gas_usage as gu
from cenote import tank
from cenote import config

import unittest
import pint
from pint.testsuite import helpers


UREG = config.UREG


class TestPlanPoint(unittest.TestCase):
    def test_construction(self):
        time = 0.0 * UREG.second
        depth = 0.0 * UREG.meter
        scr = gu.Scr(0.0 * UREG.liter / UREG.minute)
        point = gu.PlanPoint(time, depth, scr)
        self.assertEqual(time, point.time)
        self.assertEqual(point.time.units, config.TIME_UNIT)
        self.assertEqual(depth, point.depth)
        self.assertEqual(point.depth.units, config.DEPTH_UNIT)
        self.assertEqual(scr.volume_rate, point.scr.volume_rate)
        self.assertEqual(point.scr.volume_rate.units, config.VOLUME_RATE_UNIT)

    def test_wrong_units(self):
        good_time = 0.0 * UREG.second
        bad_time = UREG.parse_expression("60in^3")
        good_depth = UREG.parse_expression("12in")
        bad_depth = UREG.parse_expression("2kPa")
        scr = gu.Scr(0.0 * UREG.liter / UREG.minute)
        self.assertRaises(pint.errors.DimensionalityError, gu.PlanPoint, bad_time, good_depth, scr)
        self.assertRaises(pint.errors.DimensionalityError, gu.PlanPoint, good_time, bad_depth, scr)

    def test_negative_value(self):
        scr = gu.Scr(0.0 * UREG.liter / UREG.minute)
        self.assertRaises(ValueError, gu.PlanPoint, -1 * UREG.minute, 0 * UREG.meter, scr)
        self.assertRaises(ValueError, gu.PlanPoint, 0 * UREG.minute, -1 * UREG.meter, scr)


class Test_gas_consumed_between_points(unittest.TestCase):

    GAS_USAGE_VOLUME_TOLERANCE = 1e-3

    def test_surface_gas_usage(self):
        scr = gu.Scr(UREG.parse_expression("1 ft^3/min"))
        pt0 = gu.PlanPoint(0 * UREG.minute, depth=0 * UREG.foot, scr=scr)
        pt1 = gu.PlanPoint(1 * UREG.minute, depth=0 * UREG.foot, scr=scr)
        consumption = gu._gas_consumed_between_points(pt0, pt1, gu.Water.FRESH)
        helpers.assert_quantity_almost_equal(
            consumption, 1 * UREG.ft ** 3, self.GAS_USAGE_VOLUME_TOLERANCE
        )

    def test_depth_gas_usage_square(self):
        scr = gu.Scr(UREG.parse_expression("1 ft^3/min"))
        pt0 = gu.PlanPoint(0 * UREG.minute, depth=33.96 * UREG.foot, scr=scr)
        pt1 = gu.PlanPoint(1 * UREG.minute, depth=33.96 * UREG.foot, scr=scr)
        consumption = gu._gas_consumed_between_points(pt0, pt1, gu.Water.FRESH)
        helpers.assert_quantity_almost_equal(
            consumption, 2 * UREG.ft ** 3, self.GAS_USAGE_VOLUME_TOLERANCE
        )

        # def test_trapezoid_gas_usage(self):
        scr = gu.Scr(UREG.parse_expression("1 ft^3/min"))
        pt0 = gu.PlanPoint(0 * UREG.minute, depth=0 * UREG.foot, scr=scr)
        pt1 = gu.PlanPoint(1 * UREG.minute, depth=67.91 * UREG.foot, scr=scr)
        consumption = gu._gas_consumed_between_points(pt0, pt1, gu.Water.FRESH)
        helpers.assert_quantity_almost_equal(
            consumption, 2 * UREG.ft ** 3, self.GAS_USAGE_VOLUME_TOLERANCE
        )


class TestScr(unittest.TestCase):
    def test_construction(self):
        volume_rate = 0.1 * UREG.parse_expression("ft^3/min")
        scr = gu.Scr(volume_rate)
        self.assertEqual(scr.volume_rate, volume_rate)

    def test_construction_wrong_units(self):
        self.assertRaises(
            pint.errors.DimensionalityError,
            gu.Scr,
            50 * UREG.parse_expression("psi / min"),
        )

    def test_sac(self):
        al80 = tank.Aluminum80.create_full()
        sac = al80.SERVICE_PRESSURE / UREG.minute
        scr = gu.Scr.from_sac(sac, al80)
        self.assertEqual(scr.volume_rate, al80.service_volume() / UREG.minute)

    def test_round_trip(self):
        pressure_rate = 30 * UREG.psi / UREG.minute
        al80 = tank.Aluminum80.create_full()
        scr_from_sac = gu.Scr.from_sac(pressure_rate, al80)
        sac_from_scr = scr_from_sac.sac(al80)
        self.assertEqual(sac_from_scr, pressure_rate)

    def test_at_depth(self):
        volume_rate = 0.75 * UREG.ft ** 3 / UREG.min
        tolerance = (
            volume_rate.magnitude * 1e-2
        )  # 1% error (due to depth/pressure approximation below, not in the code)
        scr = gu.Scr(volume_rate)
        helpers.assert_quantity_almost_equal(
            scr.at_depth(0 * UREG.ft, gu.Water.FRESH), volume_rate, tolerance
        )
        helpers.assert_quantity_almost_equal(
            scr.at_depth(10.4 * UREG.meter, gu.Water.FRESH), 2 * volume_rate, tolerance
        )
        helpers.assert_quantity_almost_equal(
            scr.at_depth(10.1 * UREG.meter, gu.Water.SALT), 2 * volume_rate, tolerance
        )
        helpers.assert_quantity_almost_equal(
            scr.at_depth(20.8 * UREG.meter, gu.Water.FRESH), 3 * volume_rate, tolerance
        )
        helpers.assert_quantity_almost_equal(
            scr.at_depth(20.2 * UREG.meter, gu.Water.SALT), 3 * volume_rate, tolerance
        )


class TestResult(unittest.TestCase):
    def test_gas_usage(self):
        scr = gu.Scr(1.0 * UREG.ft ** 3 / UREG.minute)
        profile = [
            gu.PlanPoint(UREG.parse_expression("0 min"), UREG.parse_expression("0 feet"), scr),
            gu.PlanPoint(UREG.parse_expression("1 min"), UREG.parse_expression("67.91 ft"), scr),
            gu.PlanPoint(UREG.parse_expression("2 min"), UREG.parse_expression("0 feet"), scr),
        ]
        plan = gu.Plan(profile, gu.Water.FRESH)
        result = gu.Result.from_plan(plan)
        helpers.assert_quantity_almost_equal(result.consumed_volume(), 4 * UREG.foot ** 3, 1e-3)
