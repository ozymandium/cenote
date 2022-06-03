from cenote import config
from cenote.tank import Tank

import matplotlib.pyplot as plt
import numpy as np
import yaml
import pint
import enum


UREG = config.UREG


@enum.unique
class Water(enum.Enum):
    FRESH = enum.auto()
    SALT = enum.auto()


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


def water_pressure_at_depth(depth, water: Water):
    """Pressure of water, not including atmospheric pressure."""
    density = WATER_DENSITY[water]
    pressure = density * GRAVITY * depth
    return pressure.to(config.PRESSURE_UNIT)


def pressure_at_depth(depth, water=Water.FRESH):
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
    water_pressure = water_pressure_at_depth(depth, water=water)
    pressure = 1.0 * UREG.atm + water_pressure
    return pressure.to(config.PRESSURE_UNIT)


class Scr:
    """
    SCR: Surface Consumption Rate.
    Gas consumption in volume of surface-pressure gas per minute.
    This is intended to be the fundamental gas use value, with SAC being a secondary derived value.

    Members
    -------
    volume_rate : pint config.VOLUME_RATE_UNIT
    """

    def __init__(self, volume_rate):
        """
        Parameters
        ----------
        volume_rate : pint config.VOLUME_RATE_UNIT
        """
        self.volume_rate = volume_rate.to(config.VOLUME_RATE_UNIT)

    def __str__(self):
        return "{:.3f}".format(self.volume_rate)

    @staticmethod
    def from_sac(pressure_rate, tank: Tank):
        """
        Compute SCR from Surface Air Consumption (SAC).

        Parameters
        ----------
        pressure_rate : pint config.PRESSURE_RATE_UNIT
            Decrease in pressure over time for the provided tank
        tank : Tank
            The tank that coresponds to this consumption rate.
        """
        volume_rate = (
            pressure_rate.to(config.PRESSURE_RATE_UNIT)
            / tank.SERVICE_PRESSURE
            * tank.service_volume()
        )
        return Scr(volume_rate)

    def sac(self, tank: Tank):
        """SAC: Surface Air Consumption
        Consumption of gas from a specific tank measured in how quickly that tank's pressure is reduced.

        Parameters
        ----------
        pressure_rate : pint config.PRESSURE_RATE_UNIT
            Decrease in pressure over time for the provided tank
        tank : Tank
            The tank that coresponds to this consumption rate

        Returns
        -------
        pint config.PRESSURE_RATE_UNIT
        """
        return self.volume_rate * tank.SERVICE_PRESSURE / tank.service_volume()

    def at_depth(self, depth, water: Water):
        """Translate SCR to volume rate at a particular depth

        Parameters
        ----------
        depth : pint length

        Returns
        -------
        pint volume rate
        """
        scaling = pressure_at_depth(depth, water).to(UREG.atm).magnitude
        return self.volume_rate * scaling


class PlanPoint:
    """
    Members
    -------
    time : pint time
        Time elapsed since the beginning of the dive, in config.TIME_UNIT
    depth : pint distance
        Distance below surface () in config.DEPTH_UNIT
    """

    def __init__(self, time, depth, scr: Scr):
        """
        Parameters
        ----------
        time : pint time
            Time elapsed since the beginning of the dive, in config.TIME_UNIT
        depth : pint distance
            Distance below surface () in config.DEPTH_UNIT
        """
        if depth < 0 or time < 0:
            raise ValueError("Time and depth must be positive values")
        self.time = time.to(config.TIME_UNIT)
        self.depth = depth.to(config.DEPTH_UNIT)
        self.scr = scr

    def __str__(self):
        return "{:.1f}: {:.1f}".format(self.time, self.depth)


def _gas_consumed_between_points(pt0: PlanPoint, pt1: PlanPoint, water: Water):
    avg_depth = (pt0.depth + pt1.depth) * 0.5
    duration = pt1.time - pt0.time
    # assume that the SCR at the beginning of the section is the SCR for the entire section
    scr = pt0.scr
    volume_rate = scr.at_depth(avg_depth, water)
    return volume_rate * duration


class Plan:
    """
    Members
    -------
    points : list[PlanPoint]
    sections :
    """

    def __init__(self, points: list[PlanPoint], water: Water):
        self.points = points
        self.water = water

    def times(self):
        return np.array([point.time.magnitude for point in self.points])

    def depths(self):
        return np.array([point.depth.magnitude for point in self.points])


class ResultPoint:
    def __init__(self, consumed_volume):
        self.consumed_volume = consumed_volume


class Result:
    def __init__(self, points: list[ResultPoint]):
        self.points = points

    def consumed_volume(self):
        return self.points[-1].consumed_volume

    @staticmethod
    def from_plan(plan: Plan):
        consumed_volume = 0 * config.VOLUME_UNIT
        points = [ResultPoint(consumed_volume)]
        for i in range(1, len(plan.points)):
            pt0 = plan.points[i - 1]
            pt1 = plan.points[i]
            consumed_volume += _gas_consumed_between_points(pt0, pt1, plan.water)
            points.append(ResultPoint(consumed_volume))
        return Result(points)

    def consumed_volumes(self):
        return np.array([point.consumed_volume.magnitude for point in self.points])
