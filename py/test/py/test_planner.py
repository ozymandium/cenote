import unittest
import cenote
import bungee
import os
from pint.testsuite import helpers

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
PROFILE2 = os.path.join(DATA_DIR, "profile2.yaml")

class TestPlanner(unittest.TestCase):
    def test_basic(self):
        UREG = cenote.UREG
        input_plan = cenote.get_plan(PROFILE2)
        output_plan = bungee.replan(input_plan)
        profile = output_plan.profile()
        self.assertEqual(len(profile), 12)
        helpers.assert_quantity_almost_equal(profile[0].depth.value() * UREG.meter, (0.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[0].time.value(), (0.0  * UREG.minute).m)
        self.assertEqual(profile[0].tank, "Sidemount")
        helpers.assert_quantity_almost_equal(profile[1].depth.value() * UREG.meter, (150.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[1].time.value(), (5.0  * UREG.minute).m)
        self.assertEqual(profile[1].tank, "Sidemount")
        helpers.assert_quantity_almost_equal(profile[2].depth.value() * UREG.meter, (150.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[2].time.value(), (40.0 * UREG.minute).m)
        self.assertEqual(profile[2].tank, "Sidemount")
        helpers.assert_quantity_almost_equal(profile[3].depth.value() * UREG.meter, (40.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[3].time.value(), (46.0 * UREG.minute).m)
        self.assertEqual(profile[3].tank, "Deco50")
        helpers.assert_quantity_almost_equal(profile[4].depth.value() * UREG.meter, (40.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[4].time.value(), (48.0 * UREG.minute).m)
        self.assertEqual(profile[4].tank, "Deco50")
        helpers.assert_quantity_almost_equal(profile[5].depth.value() * UREG.meter, (30.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[5].time.value(), (49.0 * UREG.minute).m)
        self.assertEqual(profile[5].tank, "Deco50")
        helpers.assert_quantity_almost_equal(profile[6].depth.value() * UREG.meter, (30.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[6].time.value(), (53.0 * UREG.minute).m)
        self.assertEqual(profile[6].tank, "Deco50")
        helpers.assert_quantity_almost_equal(profile[7].depth.value() * UREG.meter, (20.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[7].time.value(), (54.0 * UREG.minute).m)
        self.assertEqual(profile[7].tank, "Deco100")
        helpers.assert_quantity_almost_equal(profile[8].depth.value() * UREG.meter, (20.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[8].time.value(), (59.0 * UREG.minute).m)
        self.assertEqual(profile[8].tank, "Deco100")
        helpers.assert_quantity_almost_equal(profile[9].depth.value() * UREG.meter, (10.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[9].time.value(), (60.0 * UREG.minute).m)
        self.assertEqual(profile[9].tank, "Deco100")
        helpers.assert_quantity_almost_equal(profile[10].depth.value() * UREG.meter, (10.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[10].time.value(), (70.0 * UREG.minute).m)
        self.assertEqual(profile[10].tank, "Deco100")
        helpers.assert_quantity_almost_equal(profile[11].depth.value() * UREG.meter, (0.0 * UREG.foot).to(UREG.meter), 0.01)
        self.assertEqual(profile[11].time.value(), (71.0 * UREG.minute).m)
        self.assertEqual(profile[11].tank, "Deco100")
    