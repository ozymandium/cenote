from cenote import water
from cenote import config


UREG = config.UREG


class Mix:
    def __init__(self, po2: float, phe: float = 0.0):
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
        self.po2 = po2
        self.phe = phe
        self.pn2 = 1.0 - po2 - phe

        # check oxygen
        if self.po2 <= 0:
            raise ValueError("pO2 must be greater than zero: {}".format(self.po2))
        if self.po2 > 1:
            raise ValueError("pO2 must be les than 1: {}".formt(self.po2))

        # check helium
        if self.phe < 0:
            raise ValueError("pHe must be greater than zero: {}".format(self.phe))
        if self.phe >= 1:
            raise ValueError("pHe must be less than 1: {}".formt(self.phe))

        # check nitrogegn
        if self.pn2 < 0:
            raise ValueError("Remaining pN2 < 0: {}".format(self.pn2))

    def po2_at_depth(self, depth, w: water.Water):
        pressure = water.pressure_from_depth(depth, w)
        return self.po2 * pressure.to(UREG.atm)

    def mod(self, max_po2: float, w: water.Water):
        multiplier = max_po2 / self.po2
        max_pressure = (multiplier * UREG.atm).to(config.PRESSURE_UNIT)
        return water.depth_from_pressure(max_pressure, w)


AIR = Mix(0.21)
EAN32 = Mix(0.32)
EAN36 = Mix(0.36)
EAN50 = Mix(0.5)
EAN75 = Mix(0.75)
O2 = Mix(1.0)
