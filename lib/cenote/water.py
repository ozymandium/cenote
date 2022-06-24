from cenote import config

import enum


UREG = config.UREG


@enum.unique
class Water(enum.Enum):
    FRESH = enum.auto()
    SALT = enum.auto()

    def __str__(self):
        return self.name


# https://bluerobotics.com/learn/pressure-depth-calculator/#hydrostatic-water-pressure-formula
WATER_DENSITY = {
    # water density varies with temperature, being more dense at lower temperatures.
    # pure water at 0C is 1000 kg/m3.
    # pick a value of pure water at 25C, since contaminnts generally decrease the density, and this
    # will offset changes due to colder water.
    # https://en.wikipedia.org/wiki/Properties_of_water
    Water.FRESH: 997.0474 * UREG.kg / UREG.meter ** 3,
    # Deep salt water has higher density (1050 kg/m3) than surface water, which varies from
    # 1020-1029 kg/m3. Pick a median value of surface seawater at 25C.
    # https://en.wikipedia.org/wiki/Seawater
    Water.SALT: 1023.6 * UREG.kg / UREG.meter ** 3,
}
# take a value close to the mean for gravity.
# https://en.wikipedia.org/wiki/Gravity_of_Earth
GRAVITY = 9.80665 * UREG.meter / UREG.sec ** 2


def water_pressure_from_depth(depth, water: Water):
    """Pressure of water, not including atmospheric pressure."""
    density = WATER_DENSITY[water]
    pressure = density * GRAVITY * depth
    return pressure.to(config.PRESSURE_UNIT)


def depth_from_water_pressure(pressure, water: Water):
    density = WATER_DENSITY[water]
    depth = pressure / (density * GRAVITY)
    return depth.to(config.DEPTH_UNIT)


def pressure_from_depth(depth, water: Water):
    """
    Get the pressure (including surface atmospheric pressure) for a given depth of sea water assuming
    that the surface is at sea level.

    Parameters
    ----------
    depth : pint distance

    Returns
    -------
    pint pressure
    """
    water_pressure = water_pressure_from_depth(depth, water=water)
    pressure = 1.0 * UREG.atm + water_pressure
    return pressure.to(config.PRESSURE_UNIT)


def depth_from_pressure(pressure, water: Water):
    """ """
    water_pressure = pressure - 1.0 * UREG.atm
    depth = depth_from_water_pressure(water_pressure, water)
    return depth.to(config.DEPTH_UNIT)
