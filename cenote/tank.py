from cenote import config


UREG = config.UREG



class Tank:
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
    def __init__(self, pressure):
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
        """Gas volume at service pressure at sea level
        """
        return cls._gas_volume_at_pressure(cls.VOLUME, cls.SERVICE_PRESSURE)

    def volume(self):
        """Volume of 1 atm gas currently stored inside the cylinder
        """
        return self._gas_volume_at_pressure(self.VOLUME, self.pressure)

    @staticmethod
    def _gas_volume_at_pressure(volume, pressure):
        """For a given fixed tank volume and pressure relative to 1 atm, find the volume of 
        1 atm gas stored inside.
        """
        return (volume * pressure.to(UREG.atm).magnitude).to(config.VOLUME_UNIT)

    @classmethod
    def create_full(cls):
        return cls(cls.SERVICE_PRESSURE)

    @classmethod
    def create_empty(cls):
        return cls(0 * config.PRESSURE_UNIT)


class Aluminum13(Tank):
    """https://www.catalinacylinders.com/product/s13/
    """
    VOLUME = 1.9 * UREG.liter
    SERVICE_PRESSURE = 3000 * UREG.psi

class Aluminum40(Tank):
    VOLUME = 5.8 * UREG.liter
    SERVICE_PRESSURE = 3000 * UREG.psi

class Aluminum80(Tank):
    VOLUME = 11.1 * UREG.liter
    SERVICE_PRESSURE = 3000 * UREG.psi

class LowPressureSteel108(Tank):
    VOLUME = 17 * UREG.liter
    SERVICE_PRESSURE = 2640 * UREG.psi


# Directory to look up Tank classes using short string.
TANKS = {
    "AL13": Aluminum13,
    "AL40": Aluminum40,
    "AL80": Aluminum80,
    "LP108": LowPressureSteel108,
}