import bungee

import pint
import yaml
import numpy as np


UREG = pint.UnitRegistry()

DEPTH_UNIT = UREG.parse_expression(bungee.get_depth_unit_str()).units
PRESSURE_UNIT = UREG.parse_expression(bungee.get_pressure_unit_str()).units
TIME_UNIT = UREG.parse_expression(bungee.get_time_unit_str()).units
VOLUME_RATE_UNIT = UREG.parse_expression(bungee.get_volume_rate_unit_str()).units

DEPTH_DISPLAY_UNIT = UREG.foot
PRESSURE_DISPLAY_UNIT = UREG.psi
TIME_DISPLAY_UNIT = UREG.minute
VOLUME_RATE_DISPLAY_UNIT = UREG.ft**3 / UREG.minute


def get_plan(path: str) -> bungee.Plan:
    with open(path, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    # Water type
    water = getattr(bungee.Water, data["water"])

    # SCR
    working_scr_pint = UREG.parse_expression(data["scr"]["work"]).to(VOLUME_RATE_UNIT)
    deco_scr_pint = UREG.parse_expression(data["scr"]["deco"]).to(VOLUME_RATE_UNIT)
    scr = bungee.Scr(
        bungee.VolumeRate(working_scr_pint.m),
        bungee.VolumeRate(deco_scr_pint.m),
    )

    # Tank loadout
    tanks = {}
    for name, info in data["tanks"].items():
        enum = getattr(bungee.Tank, info["type"])
        pressure_pint = UREG.parse_expression(info["pressure"]).to(PRESSURE_UNIT)
        pressure = bungee.Pressure(pressure_pint.m)
        mix = bungee.Mix(info["mix"]["fO2"])
        tanks[name] = bungee.TankConfig(enum, pressure, mix)

    # Plan
    plan = bungee.Plan(water, scr, tanks)

    # Profile
    for segment_data in data["profile"]:
        if "tank" in segment_data:
            plan.set_tank(segment_data["tank"])
        depth_pint = UREG.parse_expression(segment_data["depth"]).to(DEPTH_UNIT)
        depth = bungee.Depth(depth_pint.m)
        duration_pint = UREG.parse_expression(segment_data["duration"]).to(TIME_UNIT)
        duration = bungee.Time(duration_pint.m)
        plan.add_segment(duration, depth)

    plan.finalize()

    return plan


class Deco:
    def __init__(self, bungee_deco: bungee.Deco):
        self.ceiling = (bungee_deco.ceiling * DEPTH_UNIT).to(DEPTH_DISPLAY_UNIT)
        self.gradient = bungee_deco.gradient  # unitless
        self.M0s = (bungee_deco.M0s * PRESSURE_UNIT).to(UREG.atm)
        self.tissue_pressures = (bungee_deco.tissue_pressures * PRESSURE_UNIT).to(UREG.atm)
        self.ceilings = (bungee_deco.ceilings * DEPTH_UNIT).to(DEPTH_DISPLAY_UNIT)
        self.gradients = bungee_deco.gradients  # unitless


class Result:
    def __init__(self, bungee_result: bungee.Result):
        self.time = (bungee_result.time * TIME_UNIT).to(TIME_DISPLAY_UNIT)
        self.depth = (bungee_result.depth * DEPTH_UNIT).to(DEPTH_DISPLAY_UNIT)
        self.ambient_pressure = (bungee_result.ambient_pressure * PRESSURE_UNIT).to(UREG.atm)
        self.tank_pressure = {
            tank: (pressure * PRESSURE_UNIT).to(PRESSURE_DISPLAY_UNIT)
            for tank, pressure in bungee_result.tank_pressure.items()
        }
        self.deco = Deco(bungee_result.deco)


def get_result(plan: bungee.Plan):
    bungee_result = bungee.Result(plan)
    return Result(bungee_result)
