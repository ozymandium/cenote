import cenote
import unittest
import os

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
PROFILE1 = os.path.join(DATA_DIR, "profile1.json")


class TestGetPlan(unittest.TestCase):
    def test_profile1_tanks(self):
        plan = cenote.load_plan(PROFILE1)
        tanks = [point.tank for point in plan.profile()]
        self.assertEqual(
            tanks,
            [
                "bottom",  # 0
                "bottom",  # 132
                "bottom",  # 132
                "deco50",  # 70
                "bottom",  # 70
                "deco100",  # 20
                "deco100",  # 20
                "deco100",  # 10
                "deco100",  # 0
            ],
        )
