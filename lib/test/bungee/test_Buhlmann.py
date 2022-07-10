import unittest

import bungee


class TestBuhlmann(unittest.TestCase):
    def test_init(self):
        model = bungee.Model.ZHL_16A
        b = bungee.Buhlmann(model)
