import matplotlib.pyplot as plt
import numpy as np
import yaml
import pint


UREG = pint.UnitRegistry()

TIME_UNIT = UREG.minute
DEPTH_UNIT = UREG.foot
TANK_VOLUME_UNIT = UREG.liter
GAS_VOLUME_UNIT = UREG.ft**3
PRESSURE_UNIT = UREG.psi
VOLUME_RATE_UNIT = VOLUME_UNIT / TIME_UNIT
PRESSURE_RATE_UNIT = PRESSURE_UNIT / TIME_UNIT


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
    return 1.0 * UREG.atm + depth.to(UREG.foot) * SCALING


class ProfilePoint:
    """
    Members
    -------
    time : pint time
        Time elapsed since the beginning of the dive, in TIME_UNIT
    depth : pint distance
        Distance below surface () in DEPTH_UNIT
    """

    def __init__(self, time, depth):
        """
        Parameters
        ----------
        time : pint time
            Time elapsed since the beginning of the dive, in TIME_UNIT
        depth : pint distance
            Distance below surface () in DEPTH_UNIT
        """
        self.time = time.to(TIME_UNIT)
        self.depth = depth.to(DEPTH_UNIT)

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
    avg_depth :
    """

    def __init__(self, pt0: ProfilePoint, pt1: ProfilePoint):
        self.avg_depth = (pt0.depth + pt1.depth) * 0.5
        self.duration = pt1.time - pt0.time

    def gas_usage(self, rmv):
        """
        For a given surface consumption rate, determine how much gas at surface pressure is
        consumed in this section.

        TODO: find a better place for this to live.

        Parameters
        ----------
        rmv : Rmv
            Surface consumption rate.

        Returns
        -------
        pint.volume
            Volume of gas at the surface (1 atm) that is consumed during this section.
        """
        # TODO more accurate formula for this
        volume_scaling = pressure_at_depth(self.avg_depth).to(UREG.atm).magnitude
        return rmv.volume_rate * self.duration * volume_scaling


class Tank:
    """
    Members
    -------
    volume : in VOLUME_UNIT
    max_pressure : PRESSURE_UNIT
    """
    def __init__(self, gas_volume, max_pressure):
        self.tank_volume = volume.to(VOLUME_UNIT)
        self.max_pressure = max_pressure.to(PRESSURE_UNIT)
        self.max_gas_volume = self.volume * self.max_pressure.to(UREG.atm).magnitude

    @staticmethod
    def from_dict(data):
        volume = UREG.parse_expression(data["volume"])
        max_pressure = UREG.parse_expression(data["max_pressure"])
        return Tank(volume, max_pressure)

    def __str__(self):
        return "{} @ {}".format(self.gas_volume, self.max_pressure)


class Sac:

    def __init__(self, pressure_rate, tank: Tank):
        self.pressure_rate = pressure_rate.to(PRESSURE_RATE_UNIT)
        self.tank = tank
        self.rmv = Rmv(self.pressure_rate / self.tank.max_pressure * self.tank.volume)

    @staticmethod
    def from_dict(data: dict):
        pressure_rate = UREG.parse_expression(data["pressure_rate"])
        tank = Tank.from_dict(data["tank"])
        return Sac(pressure_rate, tank)
        

class Rmv:
    """
    Respiratory minute volume.
    Gas consumption in volume of surface-pressure gas per minute

    Members
    -------
    rate : in VOLUME_RATE_UNIT
    """
    def __init__(self, volume_rate):
        """
        Parameters
        ----------
        rate : in VOLUME_RATE_UNIT
        """
        self.volume_rate = volume_rate.to(VOLUME_RATE_UNIT)

    def __str__(self):
        return "{:.3f}".format(self.volume_rate)

    def sac(self, tank: Tank) -> Sac:
        pressure_rate = self.volume_rate * tank.max_pressure / tank.volume 
        return Sac(pressure_rate, tank)


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

    @staticmethod
    def from_dict(data):
        points = []
        for point_data in data:
            point = ProfilePoint.from_dict(point_data)
            if len(points) and (point.time <= points[-1].time):
                raise Exception("Time into dive must increase at every point in profile.")
            points.append(point)
        return Profile(points)

    def gas_usage(self, rmv: Rmv):
        """
        Compute the volume of surface-pressure gas that is used for this depth profile.

        Parameters
        ----------
        rmv : Rmv
            How fast gas is used on overage for this depth.

        Returns
        -------
        pint volume
        """
        volume = 0.0 * UREG.liter
        for idx in range(1, len(self.points)):
            point0 = self.points[idx - 1]
            point1 = self.points[idx]
            section = ProfileSection(point0, point1)
            volume += section.gas_usage(rmv)
        return volume


class Dive:
    """
    Members
    -------
    rmv : Rmv
    profile : Profile
    """

    def __init__(self, rmv: Rmv, profile: Profile):
        self.rmv = rmv
        self.profile = profile

    def gas_usage(self):
        """Compute the surface volume of gas used"""
        return self.profile.gas_usage(self.rmv)

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
        rmv = Rmv.from_dict(data["rmv"])
        profile = Profile.from_dict(data["profile"])
        return Dive(rmv, profile)
