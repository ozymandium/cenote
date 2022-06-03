from cenote import tank
from cenote import config

import unittest
import pint
from pint.testsuite import QuantityTestCase, helpers


UREG = config.UREG


class TestTank(unittest.TestCase, QuantityTestCase):
    def test_service_volumes(self):
        TOLERANCE = 0.05
        helpers.assert_quantity_almost_equal(tank.Aluminum13.service_volume(), 13.0 * UREG.ft**3, TOLERANCE)
        helpers.assert_quantity_almost_equal(tank.Aluminum40.service_volume(), 40.0 * UREG.ft**3, TOLERANCE)
        helpers.assert_quantity_almost_equal(tank.Aluminum80.service_volume(), 77.4 * UREG.ft**3, TOLERANCE)
        helpers.assert_quantity_almost_equal(tank.LowPressureSteel108.service_volume(), 107.8 * UREG.ft**3, TOLERANCE)


if __name__ == "__main__":
    unittest.main()
