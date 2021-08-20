import matplotlib.pyplot as plt
import numpy as np
import argparse
import yaml
import pint


UREG = pint.UnitRegistry()


class ProfilePoint:
    """
    Members
    -------
    time : in TIME_UNIT
    depth : in DEPTH_UNIT
    """

    TIME_UNIT = "minute"
    DEPTH_UNIT = "foot"

    def __init__(self, raw_data):
        self.time = UREG.parse_expression(raw_data["time"]).to(self.TIME_UNIT)
        self.depth = UREG.parse_expression(raw_data["depth"]).to(self.DEPTH_UNIT)

    def __str__(self):
        return "{:.1f}: {:.1f}".format(self.time, self.depth)


class Tank:
    """
    Members
    -------
    volume : in VOLUME_UNIT
    max_pressure : PRESSURE_UNIT
    """
    VOLUME_UNIT = "liter"
    PRESSURE_UNIT = "psi"

    def __init__(self, raw_data):
        self.volume = UREG.parse_expression(raw_data["volume"]).to(self.VOLUME_UNIT)
        self.max_pressure = UREG.parse_expression(raw_data["max_pressure"]).to(self.PRESSURE_UNIT)

    def __str__(self):
        return "{volume} @ {max_pressure}".format(volume=self.volume, max_pressure=self.max_pressure)

class Sac:
    """
    Surface air consumption in volume of surface air per minute

    Members
    -------
    rate : in VOLUME_RATE_UNIT
    """
    VOLUME_RATE_UNIT = "liter / minute"
    PRESSURE_RATE_UNIT = "psi / minute"

    def __init__(self, raw_data):
        """
        raw_data : dict of the "sac" section from the profile yaml
        """
        if "pressure_rate" in raw_data:
            if "tank" not in raw_data:
                raise Exception("pressure rate sac definition requires associated tank information.")
            press_rate = UREG.parse_expression(raw_data["pressure_rate"]).to(self.PRESSURE_RATE_UNIT)
            tank = Tank(raw_data["tank"])
            self.rate = (press_rate * tank.volume / tank.max_pressure).to(self.VOLUME_RATE_UNIT)
        elif "volume_rate" in raw_data:
            self.rate = UREG.parse_expression(raw_data["volume_rate"]).to(self.VOLUME_RATE_UNIT)
        else:
            raise Exception("sac field options are pressure_rate + tank or volume_rate")

    def __str__(self):
        return "{:.3f}".format(self.rate)


class DepthProfile:
    """
    Members
    -------
    points : list of ProfilePoint
    """
    def __init__(self, raw_data):
        self.points = []
        for raw_point_data in raw_data:
            point = ProfilePoint(raw_point_data)
            if (len(self.points) != 0) and (point.time <= self.points[-1].time):
                    raise Exception("Time into dive must increase at every point in profile.")
            self.points.append(point)


class Dive:
    """
    Members
    -------
    sac : Sac
    profile : DepthProfile
    """
    def __init__(self, raw_data):
        self.sac = Sac(raw_data["sac"])
        self.profile = DepthProfile(raw_data["profile"])
