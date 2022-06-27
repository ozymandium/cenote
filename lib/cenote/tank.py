from cenote import config
from cenote.mix import Mix

import enum


UREG = config.UREG


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

    def decrease_pressure(self, inc):
        self._pressure_change(-1.0 * inc)

    def decrease_volume(self, inc):
        self._volume_change(-1.0 * inc)

    def _pressure_change(self, inc):
        self.pressure += inc

    def _volume_change(self, inc):
        pressure_atm_magnitude = inc / self.VOLUME
        pressure_inc = (pressure_atm_magnitude * UREG.atm).to(config.PRESSURE_UNIT)
        self._pressure_change(pressure_inc)

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
    def create_full(cls, mix: Mix):
        return cls(mix=mix, pressure=cls.SERVICE_PRESSURE)

    @classmethod
    def create_empty(cls, mix: Mix):
        return cls(mix=mix, pressure=0 * config.PRESSURE_UNIT)


#
# Tank Implementations
#


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


class SidemountedLowPressureSteel108(LowPressureSteel108):
    VOLUME = 2 * LowPressureSteel108.VOLUME


class Tank(enum.Enum):
    AL13 = enum.auto()
    AL40 = enum.auto()
    AL80 = enum.auto()
    LP108 = enum.auto()
    SMLP108 = enum.auto()


# Directory to look up Tank classes using short string.
TYPES = {
    Tank.AL13: Aluminum13,
    Tank.AL40: Aluminum40,
    Tank.AL80: Aluminum80,
    Tank.LP108: LowPressureSteel108,
    Tank.SMLP108: SidemountedLowPressureSteel108
}
