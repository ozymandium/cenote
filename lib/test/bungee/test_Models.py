import unittest

import bungee


class TestModels(unittest.TestCase):
    def test_a_b(self):
        """https://en.wikipedia.org/wiki/B%C3%BChlmann_decompression_algorithm"""
        vals = [
            # ZHL16A Nitrogen
            [4.0, 1.2599, 0.5050],
            [8.0, 1.0000, 0.6514],
            [12.5, 0.8618, 0.7222],
            [18.5, 0.7562, 0.7725],
            [27.0, 0.6667, 0.8125],
            [38.3, 0.5933, 0.8434],
            [54.3, 0.5282, 0.8693],
            [77.0, 0.4701, 0.8910],
            [109.0, 0.4187, 0.9092],
            [146.0, 0.3798, 0.9222],
            [187.0, 0.3497, 0.9319],
            [239.0, 0.3223, 0.9403],
            [305.0, 0.2971, 0.9477],
            [390.0, 0.2737, 0.9544],
            [498.0, 0.2523, 0.9602],
            [635.0, 0.2327, 0.9653],
        ]
        for t, a, b in vals:
            params = bungee.CompartmentParams(t)
            self.assertAlmostEqual(params.a, a, 4)
            self.assertAlmostEqual(params.b, b, 4)
