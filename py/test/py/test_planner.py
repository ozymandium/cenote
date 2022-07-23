import unittest
import cenote
import bungee
import os

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
PROFILE2 = os.path.join(DATA_DIR, "profile2.yaml")


class TestPlanner(unittest.TestCase):
    def test_basic(self):
        input_plan = cenote.get_plan(PROFILE2)
        output_plan = bungee.replan(input_plan)
