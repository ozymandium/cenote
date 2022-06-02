from cenote import config

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


PRESSURE_AT_DEPTH_SCALING = {
    Water.FRESH: 0.96817119275 * UREG.atm / (10.0 * UREG.meter),
    Water.SALT: 0.9972163366400002 * UREG.atm / (10.0 * UREG.meter),
}


def pressure_at_depth(depth, water=Water.FRESH):
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
    scaling = PRESSURE_AT_DEPTH_SCALING[water]
    return (1.0 * UREG.atm + depth.to(UREG.foot) * scaling).to(config.PRESSURE_UNIT)


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

"""
Pre-set common tank sizes
"""
TANKS = {
    "al13": Tank(13 * UREG.ft**3, 3000 * UREG.psi),
    "al80": Tank(77.4 * UREG.ft**3, 3000 * UREG.psi),
    "lp108": Tank(108 * UREG.ft**3, 2640 * UREG.psi),
}


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


class ProfilePoint:
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


class ProfileSection:
    """Represents a period of elapsed time between two ProfilePoint instances.

    Members
    -------
    avg_depth : pint config.DEPTH_UNIT
        Mean depth of the two profile points.
    duration : pint config.TIME_UNIT
        Amount of time between the two profile points.
    scr : Scr
        Assumed the be constant throughout the entire section.s
    """

    def __init__(self, pt0: ProfilePoint, pt1: ProfilePoint):
        """
        Parameters
        ----------
        pt0 : ProfilePoint
            Beginning of the section.
        pt1 : ProfilePoint
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


class Dive:
    """
    Members
    -------
    scr : Scr
    profile : Profile
    """

    def __init__(self, profile: list[ProfilePoint]):
        self.profile = profile
        self.update_sections()

    def update_sections(self):
        """
        Compute `sections` using the data in `points`
        """
        self.sections = []
        for idx in range(1, len(self.profile)):
            section = ProfileSection(self.profile[idx - 1], self.profile[idx])
            self.sections.append(section)

    def gas_usage(self):
        """
        Compute the volume of surface-pressure gas that is used for this depth profile.

        Returns
        -------
        pint volume
        """
        volume = 0.0 * config.VOLUME_UNIT
        for section in self.sections:
            volume += section.gas_usage()
        return volume
