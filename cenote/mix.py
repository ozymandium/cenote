from cenote.water import Water, depth_from_pressure, pressure_from_depth
from cenote import config


UREG = config.UREG


class Mix:
    def __init__(self, po2: float):
        """
        Parameters
        ----------
        po2 : float
            partial pressure of oxygen at sea level
        phe : float
            partial presure of helium at sea level

        Raises
        ------
        ValueError
            If the values are WRONG!
        """
        # check oxygen
        if po2 <= 0:
            raise ValueError("pO2 must be greater than zero: {}".format(po2))
        if po2 > 1:
            raise ValueError("pO2 must be les than 1: {}".format(po2))

        self.po2 = po2
        self.pn2 = 1.0 - po2


    def po2_at_depth(self, depth, water: Water):
        pressure = pressure_from_depth(depth, water)
        return self.po2 * pressure.to(UREG.atm)

    def mod(self, max_po2: float, water: Water):
        multiplier = max_po2 / self.po2
        max_pressure = (multiplier * UREG.atm).to(config.PRESSURE_UNIT)
        return depth_from_pressure(max_pressure, water)


AIR = Mix(0.209460)
EAN32 = Mix(0.32)
EAN36 = Mix(0.36)
EAN50 = Mix(0.5)
EAN75 = Mix(0.75)
O2 = Mix(1.0)
