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
    Water.FRESH: 997.0474 * UREG.kg / UREG.meter**3,
    # Deep salt water has higher density (1050 kg/m3) than surface water, which varies from 
    # 1020-1029 kg/m3. Pick a median value of surface seawater at 25C.
    # https://en.wikipedia.org/wiki/Seawater
    Water.SALT: 1023.6 * UREG.kg / UREG.meter**3,
}
# take a value close to the mean for gravity.
# https://en.wikipedia.org/wiki/Gravity_of_Earth
GRAVITY = 9.80665 * UREG.meter / UREG.sec**2


def water_pressure_at_depth(depth, water=Water.FRESH):
    """Pressure of water, not including atmospheric pressure.
    """
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
            pressure_rate.to(config.PRESSURE_RATE_UNIT) / tank.max_pressure * tank.max_gas_volume
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
        return self.volume_rate * tank.max_pressure / tank.max_gas_volume

    def at_depth(self, depth):
        """Translate SCR to volume rate at a particular depth

        Parameters
        ----------
        depth : pint length

        Returns
        -------
        pint volume rate
        """
        scaling = pressure_at_depth(depth).to(UREG.atm).magnitude
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


class PlanSection:
    """Represents a period of elapsed time between two PlanPoint instances.

    Members
    -------
    avg_depth : pint config.DEPTH_UNIT
        Mean depth of the two profile points.
    duration : pint config.TIME_UNIT
        Amount of time between the two profile points.
    scr : Scr
        Assumed the be constant throughout the entire section.s
    """

    def __init__(self, pt0: PlanPoint, pt1: PlanPoint):
        """
        Parameters
        ----------
        pt0 : PlanPoint
            Beginning of the section.
        pt1 : PlanPoint
            End of the section. The SCR of this point will be used as the SCR for the entireity
            of the section.
        """
        self.avg_depth = (pt0.depth + pt1.depth) * 0.5
        self.duration = pt1.time - pt0.time
        # assume that the SCR at the end of the section was computed as an average of the SCR
        # throughout the section
        self.scr = pt1.scr

    def gas_usage(self):
        """
        Determine how much gas at surface pressure is
        consumed in this section.

        Returns
        -------
        pint.volume
            Volume of gas at the surface (1 atm) that is consumed during this section.
        """
        # TODO more accurate formula for this
        gas_use_rate = self.scr.at_depth(self.avg_depth)
        return gas_use_rate * self.duration


class Plan:
    """
    Members
    -------
    points : list[PlanPoint]
    sections :
    """

    def __init__(self, points: list[PlanPoint]):
        self.points = points
        # Compute `sections` using the data in `points`
        self.sections = []
        for idx in range(1, len(self.points)):
            section = PlanSection(self.points[idx - 1], self.points[idx])
            self.sections.append(section)

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
        for section in plan.sections:
            consumed_volume += section.gas_usage()
            points.append(ResultPoint(consumed_volume))
        return Result(points)

    # def consumed_volumes(self):
    #     return np.array([point.consumed_volume.magnitude for point in self.points])
