from cenote import config
import bungee

UREG = config.UREG

GRAVITY = bungee.GRAVITY_MS2 * UREG.meter / UREG.sec**2
AMBIENT_PRESSURE_SURFACE = bungee.SURFACE_PRESSURE_BAR * UREG.bar


def get_water_density(water: bungee.Water):
    return bungee.get_water_density(water) * UREG.kg / UREG.meter**3


def water_pressure_from_depth(depth, water: bungee.Water):
    """Pressure of water, not including atmospheric pressure."""
    depth_meter = depth.to(UREG.meter).magnitude
    pressure_bar = bungee.water_pressure_from_depth(depth_meter, water)
    return (pressure_bar * UREG.bar).to(config.PRESSURE_UNIT)


def depth_from_water_pressure(pressure, water: bungee.Water):
    pressure_bar = pressure.to(UREG.bar).magnitude
    depth_meter = bungee.depth_from_water_pressure(pressure_bar, water)
    return (depth_meter * UREG.meter).to(config.DEPTH_UNIT)


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
    depth_meter = depth.to(UREG.meter).magnitude
    pressure_bar = bungee.pressure_from_depth(depth_meter, water)
    return (pressure_bar * UREG.bar).to(config.PRESSURE_UNIT)


def depth_from_pressure(pressure, water: bungee.Water):
    """ """
    pressure_bar = pressure.to(UREG.bar).magnitude
    depth_meter = bungee.depth_from_pressure(pressure_bar, water)
    return (depth_meter * UREG.meter).to(config.DEPTH_UNIT)
