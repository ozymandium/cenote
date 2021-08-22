from cenote import config

import matplotlib.pyplot as plt
import numpy as np
import yaml
import pint


UREG = config.UREG


def pressure_at_depth(depth):
    """
    Get the pressure [atm] (including surface atmospheric pressure) for a given depth of sea water.
    https://oceanservice.noaa.gov/facts/pressure.html

    TODO: make this apply to fresh water

    Parameters
    ----------
    depth : pint distance

    Returns
    -------
    pint pressure
    """
    SCALING = (1.0 * UREG.atm) / (33.0 * UREG.foot)
    return (1.0 * UREG.atm + depth.to(UREG.foot) * SCALING).to(config.PRESSURE_UNIT)


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

    def __init__(self, max_gas_volume, max_pressure):
        """
        Parameters
        ----------
        max_gas_volume : in config.VOLUME_UNIT
            The volume of gas at 1 atm that the tank holds when the tank is at max_pressure.
        max_pressure : config.PRESSURE_UNIT
            The maximum pressure, and the pressure to which the max_gas_volume corresponds.
        """
        self.max_gas_volume = max_gas_volume.to(config.VOLUME_UNIT)
        self.max_pressure = max_pressure.to(config.PRESSURE_UNIT)
        self.volume = self.max_gas_volume / self.max_pressure.to(UREG.atm).magnitude

    def __str__(self):
        return "{} @ {}".format(self.gas_volume, self.max_pressure)


class Scr:
    """
    SCR: Surface Consumption Rate.
    Gas consumption in volume of surface-pressure gas per minute.
    This is intended to be the fundamental gas use value, with Sac being a secondary derived value.

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

    def sac(self, tank: Tank):
        pressure_rate = self.volume_rate * tank.max_pressure / tank.max_gas_volume
        return Sac(pressure_rate, tank)

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


class Sac:
    """
    SAC: Surface Air Consumption
    Consumption of surface-pressure gas from a specific tank measured in how quickly that
    tank's pressure is reduced.
    This is not supposed to be the primary was of computing gas use, but it is intended to be used
    often as a way of deriving SCR, because this is what a diver is able to observe easily.

    Members
    -------
    pressure_rate : pint config.PRESSURE_RATE_UNIT
        Decrease in pressure over time for the provided tank
    tank : Tank
        The tank that coresponds to this consumption rate
    scr : Scr
        The rate of consumption of 1atm gas by volume.
    """

    def __init__(self, pressure_rate, tank: Tank):
        """
        Parameters
        ----------
        pressure_rate : pint config.PRESSURE_RATE_UNIT
            Decrease in pressure over time for the provided tank
        tank : Tank
            The tank that coresponds to this consumption rate
        """
        self.pressure_rate = pressure_rate.to(config.PRESSURE_RATE_UNIT)
        self.tank = tank
        self.scr = Scr(self.pressure_rate / self.tank.max_pressure * self.tank.max_gas_volume)


class ProfilePoint:
    """
    Members
    -------
    time : pint time
        Time elapsed since the beginning of the dive, in config.TIME_UNIT
    depth : pint distance
        Distance below surface () in config.DEPTH_UNIT
    """

    def __init__(self, time, depth):
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

    def __str__(self):
        return "{:.1f}: {:.1f}".format(self.time, self.depth)


class ProfileSection:
    """Represents a period of elapsed time between two ProfilePoint instances.

    Members
    -------
    avg_depth : pint config.DEPTH_UNIT
        Mean depth of the two profile points.
    duration : pint config.TIME_UNIT
        Amount of time between the two profile points.
    """

    def __init__(self, pt0: ProfilePoint, pt1: ProfilePoint):
        self.avg_depth = (pt0.depth + pt1.depth) * 0.5
        self.duration = pt1.time - pt0.time

    def gas_usage(self, scr: Scr):
        """
        For a given surface consumption rate, determine how much gas at surface pressure is
        consumed in this section.

        TODO: find a better place for this to live.

        Parameters
        ----------
        scr : Scr
            Surface consumption rate.

        Returns
        -------
        pint.volume
            Volume of gas at the surface (1 atm) that is consumed during this section.
        """
        # TODO more accurate formula for this
        gas_use_rate = scr.at_depth(self.avg_depth)
        return gas_use_rate * self.duration


class Profile:
    """
    Members
    -------
    points : list of ProfilePoint
    """

    def __init__(self, points: list[ProfilePoint]):
        if len(points) < 2:
            raise Exception("Need at least 2 points")
        if points[0].time != 0:
            raise Exception("starting point time must be zero")
        for idx in range(1, len(points)):
            if points[idx - 1].time >= points[idx].time:
                raise Exception("Time into dive must increase at every point in profile.")
        self.points = points


class Dive:
    """
    Members
    -------
    scr : Scr
    profile : Profile
    """

    def __init__(self, scr: Scr, profile: Profile):
        self.scr = scr
        self.profile = profile

    def gas_usage(self):
        """
        Compute the volume of surface-pressure gas that is used for this depth profile.

        Returns
        -------
        pint volume
        """
        volume = 0.0 * config.VOLUME_UNIT
        for idx in range(1, len(self.profile.points)):
            section = ProfileSection(self.profile.points[idx - 1], self.profile.points[idx])
            volume += section.gas_usage(self.scr)
        return volume
