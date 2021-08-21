import matplotlib.pyplot as plt
import numpy as np
import yaml
import pint


UREG = pint.UnitRegistry()

TIME_UNIT = UREG.minute
DEPTH_UNIT = UREG.foot
VOLUME_UNIT = UREG.liter
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


class DepthProfilePoint:
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
        return DepthProfilePoint(time, depth)


class DepthProfileSection:
    """Represents a period of elapsed time between two DepthProfilePoint instances.

    Members
    avg_depth :
    """

    def __init__(self, pt0: DepthProfilePoint, pt1: DepthProfilePoint):
        self.avg_depth = (pt0.depth + pt1.depth) * 0.5
        self.duration = pt1.time - pt0.time

    def gas_usage(self, scr):
        """
        For a given surface consumption rate, determine how much gas at surface pressure is
        consumed in this section.

        TODO: find a better place for this to live.

        Parameters
        ----------
        scr : SurfaceConsumptionRate
            Surface consumption rate.

        Returns
        -------
        pint.volume
            Volume of gas at the surface (1 atm) that is consumed during this section.
        """
        # TODO more accurate formula for this
        volume_scaling = pressure_at_depth(self.avg_depth).to(UREG.atm).magnitude
        return scr.rate * self.duration * volume_scaling


class Tank:
    """
    Members
    -------
    volume : in VOLUME_UNIT
    max_pressure : PRESSURE_UNIT
    """

    def __init__(self, volume, max_pressure):
        self.volume = volume
        self.max_pressure = max_pressure

    @staticmethod
    def from_dict(data):
        volume = UREG.parse_expression(data["volume"]).to(VOLUME_UNIT)
        max_pressure = UREG.parse_expression(data["max_pressure"]).to(PRESSURE_UNIT)
        return Tank(volume, max_pressure)

    def __str__(self):
        return "{} @ {}".format(self.volume, self.max_pressure)


class SurfaceConsumptionRate:
    """
    Surface air consumption in volume of surface air per minute

    Members
    -------
    rate : in VOLUME_RATE_UNIT
    """

    def __init__(self, rate):
        """
        Parameters
        ----------
        rate : in VOLUME_RATE_UNIT
        """
        self.rate = rate.to(VOLUME_RATE_UNIT)

    @staticmethod
    def from_dict(data):
        """
        Parameters
        ----------
        data : dict
            of the "sac" section from the profile yaml

        Returns
        -------
        SurfaceConsumptionRate
        """
        if "volume_rate" in data:
            volume_rate = UREG.parse_expression(data["volume_rate"]).to(
                VOLUME_RATE_UNIT
            )
        elif "pressure_rate" in data:
            if "tank" not in data:
                raise Exception(
                    "pressure rate SCR requires associated tank information."
                )
            pressure_rate = UREG.parse_expression(data["pressure_rate"]).to(
                PRESSURE_RATE_UNIT
            )
            tank = Tank.from_dict(data["tank"])
            volume_rate = (pressure_rate * tank.volume / tank.max_pressure).to(
                VOLUME_RATE_UNIT
            )
        else:
            raise Exception("sac field options are pressure_rate + tank or volume_rate")
        return SurfaceConsumptionRate(volume_rate)

    def __str__(self):
        return "{:.3f}".format(self.rate)


class DepthProfile:
    """
    Members
    -------
    points : list of DepthProfilePoint
    """

    def __init__(self, points):
        self.points = points

    @staticmethod
    def from_dict(data):
        points = []
        for point_data in data:
            point = DepthProfilePoint.from_dict(point_data)
            if len(points) and (point.time <= points[-1].time):
                raise Exception(
                    "Time into dive must increase at every point in profile."
                )
            points.append(point)
        return DepthProfile(points)

    def gas_usage(self, scr):
        """
        Compute the volume of surface-pressure gas that is used for this depth profile.

        Parameters
        ----------
        scr : SurfaceConsumptionRate
            How fast gas is used on overage for this depth.

        Returns
        -------
        pint volume
        """
        volume = 0.0 * UREG.liter
        for idx in range(1, len(self.points)):
            point0 = self.points[idx - 1]
            point1 = self.points[idx]
            section = DepthProfileSection(point0, point1)
            volume += section.gas_usage(scr)
        return volume


class Dive:
    """
    Members
    -------
    scr : SurfaceConsumptionRate
    profile : DepthProfile
    """

    def __init__(self, scr, profile):
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
        scr = SurfaceConsumptionRate.from_dict(data["scr"])
        profile = DepthProfile.from_dict(data["profile"])
        return Dive(scr, profile)
