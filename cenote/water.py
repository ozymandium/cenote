from cenote import config
import bungee

UREG = config.UREG

GRAVITY = bungee.GRAVITY_MS2 * UREG.meter / UREG.sec ** 2
AMBIENT_PRESSURE_SURFACE = bungee.SURFACE_PRESSURE_BAR * UREG.bar


def get_water_density(water: bungee.Water):
    return bungee.get_water_density(water) * UREG.kg / UREG.meter ** 3


def water_pressure_from_depth(depth, water: bungee.Water):
    """Pressure of water, not including atmospheric pressure."""
    density = get_water_density(water)
    pressure = density * GRAVITY * depth
    return pressure.to(config.PRESSURE_UNIT)


def depth_from_water_pressure(pressure, water: bungee.Water):
    density = get_water_density(water)
    depth = pressure / (density * GRAVITY)
    return depth.to(config.DEPTH_UNIT)


def pressure_from_depth(depth, water: bungee.Water):
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
    pressure = AMBIENT_PRESSURE_SURFACE + water_pressure
    return pressure.to(config.PRESSURE_UNIT)


def depth_from_pressure(pressure, water: bungee.Water):
    """ """
    water_pressure = pressure - AMBIENT_PRESSURE_SURFACE
    depth = depth_from_water_pressure(water_pressure, water)
    return depth.to(config.DEPTH_UNIT)
