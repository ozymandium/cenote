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
    https://oceanservice.noaa.gov/facts/pressure.html

    TODO: make this apply to fresh water

    """
    SCALING = (1.0 * UREG.atm) / (33.0 * UREG.foot)
    return 1.0 * UREG.atm + depth * SCALING


class DepthProfilePoint:
    """
    Members
    -------
    time : Time elapsed since the beginning of the dive, in TIME_UNIT
    depth : Distance below surface () in DEPTH_UNIT
    """


    def __init__(self, raw_data):
        self.time = UREG.parse_expression(raw_data["time"]).to(TIME_UNIT)
        self.depth = UREG.parse_expression(raw_data["depth"]).to(DEPTH_UNIT)

    def __str__(self):
        return "{:.1f}: {:.1f}".format(self.time, self.depth)


class DepthProfileSection:  
    """Represents a period of elapsed time between two DepthProfilePoint instances.

    Members
    avg_depth : 
    """
    def __init__(self, pt0, pt1):
        self.avg_depth = (pt0.depth + pt1.depth) * 0.5
        self.elapsed_time = pt1.time - pt0.time

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
        return scr.rate * self.elapsed_time * volume_scaling

class Tank:
    """
    Members
    -------
    volume : in VOLUME_UNIT
    max_pressure : PRESSURE_UNIT
    """

    def __init__(self, raw_data):
        self.volume = UREG.parse_expression(raw_data["volume"]).to(VOLUME_UNIT)
        self.max_pressure = UREG.parse_expression(raw_data["max_pressure"]).to(PRESSURE_UNIT)

    def __str__(self):
        return "{volume} @ {max_pressure}".format(volume=self.volume, max_pressure=self.max_pressure)


class SurfaceConsumptionRate:
    """
    Surface air consumption in volume of surface air per minute

    Members
    -------
    rate : in VOLUME_RATE_UNIT
    """

    def __init__(self, raw_data):
        """
        raw_data : dict of the "sac" section from the profile yaml
        """
        if "pressure_rate" in raw_data:
            if "tank" not in raw_data:
                raise Exception("pressure rate sac definition requires associated tank information.")
            press_rate = UREG.parse_expression(raw_data["pressure_rate"]).to(PRESSURE_RATE_UNIT)
            tank = Tank(raw_data["tank"])
            self.rate = (press_rate * tank.volume / tank.max_pressure).to(VOLUME_RATE_UNIT)
        elif "volume_rate" in raw_data:
            self.rate = UREG.parse_expression(raw_data["volume_rate"]).to(VOLUME_RATE_UNIT)
        else:
            raise Exception("sac field options are pressure_rate + tank or volume_rate")

    def __str__(self):
        return "{:.3f}".format(self.rate)


class DepthProfile:
    """
    Members
    -------
    points : list of DepthProfilePoint
    """
    def __init__(self, raw_data):
        self.points = []
        for raw_point_data in raw_data:
            point = DepthProfilePoint(raw_point_data)
            if (len(self.points) != 0) and (point.time <= self.points[-1].time):
                    raise Exception("Time into dive must increase at every point in profile.")
            self.points.append(point)

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
    def __init__(self, raw_data):
        self.scr = SurfaceConsumptionRate(raw_data["sac"])
        self.profile = DepthProfile(raw_data["profile"])

    def gas_usage(self):
        """Compute the surface volume of gas used
        """
        return self.profile.gas_usage(self.scr)
