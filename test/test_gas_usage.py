from cenote import gas_usage as gu
from cenote import tank
from cenote import config

import unittest
import pint
from pint.testsuite import QuantityTestCase, helpers


UREG = config.UREG


class TestPressureAtDepth(unittest.TestCase, QuantityTestCase):
    """https://bluerobotics.com/learn/pressure-depth-calculator/
    """
    def test_almost(self):
        VALUES = {
            gu.Water.FRESH: {
                100 * UREG.meter: 141.81 * UREG.psi,
                32.81 * UREG.ft: 14.18 * UREG.psi,
            },
            gu.Water.SALT: {
                100 * UREG.meter: 145.59 * UREG.psi,
                32.81 * UREG.ft: 14.56 * UREG.psi,
            },
        }
        PRESSURE_TOLERANCE = (1e-3 * UREG.atm).to(UREG.psi).magnitude

        for water in VALUES:
            for depth in VALUES[water]:
                expected_water_pressure = VALUES[water][depth]
                expected_pressure = expected_water_pressure + 1 * UREG.atm
                water_pressure = gu.water_pressure_at_depth(depth, water)
                pressure = gu.pressure_at_depth(depth, water)
                helpers.assert_quantity_almost_equal(
                    water_pressure, 
                    expected_water_pressure, 
                    PRESSURE_TOLERANCE)
                helpers.assert_quantity_almost_equal(
                    pressure, 
                    expected_pressure, 
                    PRESSURE_TOLERANCE)


class TestPlanPoint(unittest.TestCase, QuantityTestCase):
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
        self.assertRaises(
            pint.errors.DimensionalityError, gu.PlanPoint, bad_time, good_depth, scr
        )
        self.assertRaises(
            pint.errors.DimensionalityError, gu.PlanPoint, good_time, bad_depth, scr
        )

    def test_negative_value(self):
        scr = gu.Scr(0.0 * UREG.liter / UREG.minute)
        self.assertRaises(ValueError, gu.PlanPoint, -1 * UREG.minute, 0 * UREG.meter, scr)
        self.assertRaises(ValueError, gu.PlanPoint, 0 * UREG.minute, -1 * UREG.meter, scr)


# class PlanSection(PintTest):

#     # we define stuff in liters and the moduel does stuff in ft^3 (maybe, who knows, it's configurable)
#     # so give it a little numerical round off wiggle room.
#     GAS_USAGE_VOLUME_TOLERANCE = 1e-12 * config.VOLUME_UNIT

#     def test_construction(self):
#         pt0 = gu.PlanPoint(
#             1 * UREG.minute, depth=12 * UREG.foot, scr=gu.Scr(1 * UREG.liter / UREG.minute)
#         )
#         pt1 = gu.PlanPoint(
#             2 * UREG.minute, depth=15 * UREG.foot, scr=gu.Scr(2 * UREG.liter / UREG.minute)
#         )
#         section = gu.PlanSection(pt0, pt1)
#         self.assertEqual(section.avg_depth, 13.5 * UREG.foot)
#         self.assertEqual(section.duration, 60 * UREG.second)
#         self.assertEqual(section.scr.volume_rate, pt1.scr.volume_rate)

#     def test_surface_gas_usage(self):
#         scr = gu.Scr(UREG.parse_expression("1.5 l/min"))
#         pt0 = gu.PlanPoint(0 * UREG.minute, depth=0 * UREG.foot, scr=scr)
#         pt1 = gu.PlanPoint(2.5 * UREG.minute, depth=0 * UREG.foot, scr=scr)
#         section = gu.PlanSection(pt0, pt1)
#         consumption = section.gas_usage()
#         helpers.assert_quantity_almost_equal(consumption, 3.75 * UREG.liter, self.GAS_USAGE_VOLUME_TOLERANCE)

#     # def test_depth_gas_usage_square(self):
#     #     scr = gu.Scr(UREG.parse_expression("1.5 l/min"))
#     #     pt0 = gu.PlanPoint(0 * UREG.minute, depth=66 * UREG.foot, scr=scr)
#     #     pt1 = gu.PlanPoint(2.5 * UREG.minute, depth=66 * UREG.foot, scr=scr)
#     #     section = gu.PlanSection(pt0, pt1)
#     #     consumption = section.gas_usage()
#     #     helpers.assert_quantity_almost_equal(
#     #         consumption, 3 * 3.75 * UREG.liter, self.GAS_USAGE_VOLUME_TOLERANCE
#     #     )

#     # def test_trapezoid_gas_usage(self):
#     #     scr = gu.Scr(UREG.parse_expression("1.5 l/min"))
#     #     pt0 = gu.PlanPoint(0 * UREG.minute, depth=0 * UREG.foot, scr=scr)
#     #     pt1 = gu.PlanPoint(2.5 * UREG.minute, depth=66 * UREG.foot, scr=scr)
#     #     section = gu.PlanSection(pt0, pt1)
#     #     consumption = section.gas_usage()
#     #     helpers.assert_quantity_almost_equal(
#     #         consumption, 2 * 3.75 * UREG.liter, self.GAS_USAGE_VOLUME_TOLERANCE
#     #     )


class TestScr(unittest.TestCase, QuantityTestCase):
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
        volume_rate = 0.75 * UREG.ft**3 / UREG.min
        tolerance = volume_rate.magnitude * 1e-2 # 1% error (due to depth/pressure approximation below, not in the code)
        scr = gu.Scr(volume_rate)
        helpers.assert_quantity_almost_equal(scr.at_depth(0 * UREG.ft, gu.Water.FRESH), volume_rate, tolerance)
        helpers.assert_quantity_almost_equal(scr.at_depth(10.4 * UREG.meter, gu.Water.FRESH), 2 * volume_rate, tolerance)
        helpers.assert_quantity_almost_equal(scr.at_depth(10.1 * UREG.meter, gu.Water.SALT), 2 * volume_rate, tolerance)
        # helpers.assert_quantity_almost_equal(scr.at_depth(20 * UREG.meter), 3 * volume_rate, tolerance)

    # def test_from_sac(self):
    #     pressure_rate = UREG.parse_expression("30psi/min")
    #     max_gas_volume = 3000 * UREG.liter
    #     max_pressure = max_pressure = 3000 * UREG.psi
    #     tank = gu.Tank(max_gas_volume, max_pressure)
    #     scr = gu.Scr.from_sac(pressure_rate, tank)
    #     self.assertEqual(scr.volume_rate, 30 * UREG.liter / UREG.minute)

    # def test_from_sac_wrong_units(self):
    #     bad_pressure_rate = UREG.parse_expression("30inch/min")
    #     max_gas_volume = 3000 * UREG.liter
    #     max_pressure = max_pressure = 3000 * UREG.psi
    #     tank = gu.Tank(max_gas_volume, max_pressure)
    #     self.assertRaises(pint.errors.DimensionalityError, gu.Scr.from_sac, bad_pressure_rate, tank)


# class TestPlan(PintTest):
#     def test_gas_usage(self):
#         scr = gu.Scr(1.0 * UREG.liter / UREG.minute)
#         profile = [
#             gu.PlanPoint(UREG.parse_expression("0 min"), UREG.parse_expression("0 feet"), scr),
#             gu.PlanPoint(UREG.parse_expression("1 min"), UREG.parse_expression("0 feet"), scr),
#             gu.PlanPoint(UREG.parse_expression("2 min"), UREG.parse_expression("66 feet"), scr),
#         ]
#         plan = gu.Plan(profile)
#         helpers.assert_quantity_almost_equal(plan.gas_usage(), 3.0 * UREG.liter, 1e-12 * config.VOLUME_UNIT)


# if __name__ == "__main__":
#     unittest.main()
