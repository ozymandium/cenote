from scuba import config

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
        self.max_pressure = max_pressure.to(config.PRESSURE_UNIT)
        self.max_gas_volume = max_gas_volume.to(config.VOLUME_UNIT)
        self.volume = self.max_gas_volume / self.max_pressure.to(UREG.atm).magnitude

    @staticmethod
    def from_dict(data):
        max_gas_volume = UREG.parse_expression(data["max_gas_volume"])
        max_pressure = UREG.parse_expression(data["max_pressure"])
        return Tank(max_gas_volume, max_pressure)

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


class Sac:
    """
    SAC: Surface Air Consumption
    Consumption of surface-pressure gas from a specific tank measured in how quickly that 
    tank's pressure is reduced. 
    This is not supposed to be the primary was of computing gas use, but it is intended to be used
    often as a way of driving SCR, because this is what a diver is able to observe easilyh.

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

    @staticmethod
    def from_dict(data: dict):
        pressure_rate = UREG.parse_expression(data["pressure_rate"])
        tank = Tank.from_dict(data["tank"])
        return Sac(pressure_rate, tank)

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

    @staticmethod
    def from_dict(data):
        time = UREG.parse_expression(data["time"])
        depth = UREG.parse_expression(data["depth"])
        return ProfilePoint(time, depth)


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
        volume_scaling = pressure_at_depth(self.avg_depth).to(UREG.atm).magnitude
        return scr.volume_rate * self.duration * volume_scaling


class Profile:
    """
    Members
    -------
    points : list of ProfilePoint
    """

    def __init__(self, points: list[ProfilePoint]):
        if len(points) < 2:
            raise Exception("Need at least 2 points")
        self.points = points
        # check time increase
        for idx in range(1, len(self.points)):
            if self.points[idx - 1].time >= self.points[idx].time:
                raise Exception("Time into dive must increase at every point in profile.")

    @staticmethod
    def from_dict(data):
        points = []
        for point_data in data:
            point = ProfilePoint.from_dict(point_data)
            points.append(point)
        return Profile(points)

    def gas_usage(self, scr: Scr):
        """
        Compute the volume of surface-pressure gas that is used for this depth profile.

        Parameters
        ----------
        scr : Scr
            How fast gas is used on overage for this depth.

        Returns
        -------
        pint volume
        """
        volume = 0.0 * config.VOLUME_UNIT
        for idx in range(1, len(self.points)):
            section = ProfileSection(self.points[idx - 1], self.points[idx])
            volume += section.gas_usage(scr)
        return volume


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
        """Compute the surface volume of gas used"""
        return self.profile.gas_usage(self.scr)

    @staticmethod
    def from_yaml(path):
        """
        Parameters
        ----------
        path : str
            File path to a YAML file. Specification set by example for now :/

        Returns
        -------
        Dive
        """
        with open(path, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        return Dive.from_dict(data)

    @staticmethod
    def from_dict(data):
        """
        Parameters
        ----------
        data : dict
            Parsed full YAML for a dive.

        Returns
        -------
        Dive
        """
        # try to use SCR
        if "scr" in data:
            scr = Scr(volume_rate=UREG.parse_expression(data["scr"]))
        # if no SCR, try to use SAC
        else:
            if "sac" not in data:
                raise Exception("Must provid either `scr` or `sac` section.")
            sac = Sac.from_dict(data["sac"])
            scr = sac.scr
        profile = Profile.from_dict(data["profile"])
        return Dive(scr, profile)
