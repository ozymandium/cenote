from cenote import config
from cenote import water

import enum


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


class TankBase:
    """
    Members
    -------
    volume : in config.VOLUME_UNIT
        The absolute volume of the tank itself
    max_gas_volume : in config.VOLUME_UNIT
        The volume of gas at 1 atm that the tank holds when the tank is at max_pressure.
    max_pressure : config.PRESSURE_UNIT
        The maximum pressure, and the pressure to which the max_gas_volume corresponds.
    """

    # Accounts for the differences between ideal capacity and true capacity
    # https://www.divegearexpress.com/library/articles/calculating-scuba-cylinder-capacities
    # Pick a value with perfect capacity and let implementations handle non-ideal conditions.
    Z_FACTOR = 1.0

    def __init__(self, mix: Mix, pressure):
        self.mix = mix
        self.pressure = pressure.to(config.PRESSURE_UNIT)

    def increase_pressure(self, inc):
        self.pressure_change(inc)

    def decrease_pressure(self, inc):
        self.pressure_change(-1.0 * inc)

    def increase_volume(self, inc):
        self.volume_change(inc)

    def decrease_volume(self, inc):
        self.volume_change(-1.0 * inc)

    def pressure_change(self, inc):
        self.pressure += inc

    def volume_change(self, inc):
        pressure_atm_magnitude = inc / self.VOLUME
        pressure_inc = (pressure_atm_magnitude * UREG.atm).to(config.PRESSURE_UNIT)
        self.pressure_change(pressure_inc)

    @classmethod
    def service_volume(cls):
        """Gas volume at service pressure at sea level"""
        return cls._gas_volume_at_pressure(cls.VOLUME, cls.SERVICE_PRESSURE, cls.Z_FACTOR)

    def volume(self):
        """Volume of 1 atm gas currently stored inside the cylinder"""
        return self._gas_volume_at_pressure(self.VOLUME, self.pressure, self.Z_FACTOR)

    @staticmethod
    def _gas_volume_at_pressure(volume, pressure, z):
        """For a given fixed tank volume and pressure relative to 1 atm, find the volume of
        1 atm gas stored inside.

        https://www.divegearexpress.com/library/articles/calculating-scuba-cylinder-capacities
        """
        pressure_scaling = pressure / (1 * UREG.atm).to(config.PRESSURE_UNIT)
        ideal_capacity = volume * pressure_scaling
        capacity = ideal_capacity / z
        return capacity.to(config.VOLUME_UNIT)

    @classmethod
    def create_full(cls):
        return cls(cls.SERVICE_PRESSURE)

    @classmethod
    def create_empty(cls):
        return cls(0 * config.PRESSURE_UNIT)


class Aluminum13(TankBase):
    """https://www.catalinacylinders.com/product/s13/"""

    VOLUME = 1.9 * UREG.liter
    SERVICE_PRESSURE = 3000 * UREG.psi
    Z_FACTOR = 1.054


class Aluminum40(TankBase):
    """https://www.catalinacylinders.com/product/s40/"""

    VOLUME = 5.8 * UREG.liter
    SERVICE_PRESSURE = 3000 * UREG.psi
    Z_FACTOR = 1.045


class Aluminum80(TankBase):
    """https://www.catalinacylinders.com/product/s80/"""

    VOLUME = (11.1 * UREG.liter).to(config.VOLUME_UNIT)
    SERVICE_PRESSURE = 3000 * UREG.psi
    Z_FACTOR = 1.0337


class LowPressureSteel108(TankBase):
    """Can't find specs for this. z factor of 1 gives under 108."""

    VOLUME = 17 * UREG.liter
    SERVICE_PRESSURE = 2640 * UREG.psi


class Tank(enum.Enum):
    AL13 = enum.auto()
    AL40 = enum.auto()
    AL80 = enum.auto()
    LP108 = enum.auto()


# Directory to look up Tank classes using short string.
TYPES = {
    Tank.AL13: Aluminum13,
    Tank.AL40: Aluminum40,
    Tank.AL80: Aluminum80,
    Tank.LP108: LowPressureSteel108,
}
