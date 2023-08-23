import bungee

import pint
import json
import numpy as np


UREG = pint.UnitRegistry()

DEPTH_UNIT = UREG.parse_units(bungee.get_depth_unit_str())
PRESSURE_UNIT = UREG.parse_units(bungee.get_pressure_unit_str())
TIME_UNIT = UREG.parse_units(bungee.get_time_unit_str())
VOLUME_RATE_UNIT = UREG.parse_units(bungee.get_volume_rate_unit_str())
VOLUME_UNIT = UREG.parse_units(bungee.get_volume_unit_str())


def plan_from_file(path: str) -> bungee.Plan:
    with open(path, "r") as f:
        blob = f.read()
    return plan_from_json_str(blob)


def plan_from_json_str(blob: str) -> bungee.Plan:
    data = json.loads(blob)
    return plan_from_dict(data)


def plan_from_dict(data: dict) -> bungee.Plan:
    """
    user_input : str
        either a path to a yaml file (is_path = True),
        or the contents of a yaml file (is_path = False).
    """
    # Water type
    water = getattr(bungee.Water, data["water"])

    # Gradient Factors
    gf = bungee.GradientFactor(data["gf"]["low"], data["gf"]["high"])

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
        enum = getattr(bungee.TankType, info["type"])
        pressure_pint = UREG.parse_expression(info["pressure"]).to(PRESSURE_UNIT)
        pressure = bungee.Pressure(pressure_pint.m)
        mix = bungee.Mix(info["mix"]["fO2"])
        tanks[name] = bungee.TankConfig(enum, pressure, mix)

    # Plan
    plan = bungee.Plan(water, gf, scr, tanks)

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
        self.ceiling = bungee_deco.ceiling * DEPTH_UNIT
        self.gradient = (bungee_deco.gradient * UREG.dimensionless).to(UREG.percent)
        self.M0s = bungee_deco.M0s * PRESSURE_UNIT
        self.tissue_pressures = bungee_deco.tissue_pressures * PRESSURE_UNIT
        self.ceilings = bungee_deco.ceilings * DEPTH_UNIT
        self.gradients = (bungee_deco.gradients * UREG.dimensionless).to(UREG.percent)


class Result:
    def __init__(self, bungee_result: bungee.Result):
        self.time = bungee_result.time * TIME_UNIT
        self.depth = bungee_result.depth * DEPTH_UNIT
        self.ambient_pressure = bungee_result.ambient_pressure * PRESSURE_UNIT
        self.tank_pressure = {
            tank: pressure * PRESSURE_UNIT for tank, pressure in bungee_result.tank_pressure.items()
        }
        self.deco = Deco(bungee_result.deco)


def get_result(plan: bungee.Plan) -> Result:
    bungee_result = bungee.Result(plan)
    return Result(bungee_result)
