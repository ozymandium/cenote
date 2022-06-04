from cenote import config
from cenote.tank import TankBase
from cenote.tank import TYPES as TANK_TYPES

import matplotlib.pyplot as plt
import numpy as np
import yaml
import pint
import enum
from copy import deepcopy


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
    def from_sac(pressure_rate, tank: TankBase):
        """
        Compute SCR from Surface Air Consumption (SAC).

        Parameters
        ----------
        pressure_rate : pint config.PRESSURE_RATE_UNIT
            Decrease in pressure over time for the provided tank
        tank : TankBase
            The tank that coresponds to this consumption rate.
        """
        volume_rate = (
            pressure_rate.to(config.PRESSURE_RATE_UNIT)
            / tank.SERVICE_PRESSURE
            * tank.service_volume()
        )
        return Scr(volume_rate)

    def sac(self, tank: TankBase):
        """SAC: Surface Air Consumption
        Consumption of gas from a specific tank measured in how quickly that tank's pressure is reduced.

        Parameters
        ----------
        pressure_rate : pint config.PRESSURE_RATE_UNIT
            Decrease in pressure over time for the provided tank
        tank : TankBase
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

    def __init__(self, time, depth, scr: Scr, tank_name: str):
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
        self.tank_name = tank_name

    def __str__(self):
        return "{time:.1f} {depth:.1f} {scr} {tank}".format(
            time=self.time, depth=self.depth, scr=self.scr, tank=self.tank_name
        )


def _usage_between_points(pt0: PlanPoint, pt1: PlanPoint, water: Water):
    avg_depth = (pt0.depth + pt1.depth) * 0.5
    duration = pt1.time - pt0.time
    # assume that the SCR at the beginning of the section is the SCR for the entire section
    scr = pt0.scr
    volume_rate = scr.at_depth(avg_depth, water)
    return volume_rate * duration


class TankInfo:
    def __init__(self, enum, pressure):
        self.enum = enum
        self.pressure = pressure


class Plan:
    """
    Members
    -------
    points : list[PlanPoint]
    """

    def __init__(self, water: Water, scr: Scr, tank_info: dict[str, TankInfo]):
        self.water = water
        self.scr = scr
        self.tank_info = tank_info
        self.points = []

        # check that time is strictly increasing
        assert np.all(np.diff(self.times()) > 0)

    def add_point(self, time, depth, scr=None, tank_name=None):
        """
        if scr is not provided, it is copied from the dive plan default.
        tank name is either specified or copied over from the last point.
        """
        if scr is None:
            scr = self.scr

        if tank_name is None:
            tank_name = self.back().tank_name
        if tank_name not in self.tank_info:
            raise ValueError(
                "Tank name `{}` not found. Available names: {}".format(
                    tank_name, self.tank_info.keys()
                )
            )

        point = PlanPoint(time, depth, scr, tank_name)
        self.points.append(point)

    def times(self):
        return np.array([point.time.magnitude for point in self.points])

    def depths(self):
        return np.array([point.depth.magnitude for point in self.points])

    def back(self):
        if not len(self.points):
            raise RuntimeError("No points have been added.")
        return self.points[-1]


class ResultPoint:
    def __init__(self, usage, pressure):
        self.usage = deepcopy(usage)
        self.pressure = pressure


class Result:
    def __init__(self, plan: Plan):
        self.tank_names = plan.tank_info.keys()
        # initialize tank objects
        tanks = {
            name: TANK_TYPES[plan.tank_info[name].enum](plan.tank_info[name].pressure)
            for name in self.tank_names
        }
        # keep track of usage for each tank over time, will copy this to each result point
        usage = {name: 0.0 * config.VOLUME_UNIT for name in self.tank_names}
        # compute usage for each section between points
        self.points = [ResultPoint(usage, {name: tanks[name].pressure for name in self.tank_names})]
        for i in range(1, len(plan.points)):
            pt0 = plan.points[i - 1]
            pt1 = plan.points[i]
            tank_name = pt0.tank_name
            this_usage = _usage_between_points(pt0, pt1, plan.water)
            tanks[tank_name].decrease_volume(this_usage)
            usage[tank_name] += this_usage
            # generate a pressure dict
            pressure = {name: tanks[name].pressure for name in self.tank_names}
            self.points.append(ResultPoint(usage, pressure))

    def back(self):
        return self.points[-1]

    def usages(self):
        return {
            name: np.array([point.usage[name].magnitude for point in self.points])
            for name in self.tank_names
        }

    def pressures(self):
        return {
            name: np.array([point.pressure.magnitude for point in self.points])
            for name in self.tank_names
        }
