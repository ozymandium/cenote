from cenote import tank
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


class TestTank(PintTest):
    def test_service_volumes(self):
        TOLERANCE = 0.05 * UREG.ft**3
        self.assertPintAlmostEqual(tank.Aluminum13.service_volume(), 13.0 * UREG.ft**3, TOLERANCE)
        self.assertPintAlmostEqual(tank.Aluminum40.service_volume(), 40.0 * UREG.ft**3, TOLERANCE)
        self.assertPintAlmostEqual(tank.Aluminum80.service_volume(), 77.4 * UREG.ft**3, TOLERANCE)
        self.assertPintAlmostEqual(tank.LowPressureSteel108.service_volume(), 107.8 * UREG.ft**3, TOLERANCE)


if __name__ == "__main__":
    unittest.main()
