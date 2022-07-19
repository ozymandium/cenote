import cenote
import bungee
import pint
import yaml


UREG = pint.UnitRegistry()

DEPTH_UNIT = UREG.parse_expression(bungee.get_depth_unit_str()).units
PRESSURE_UNIT = UREG.parse_expression(bungee.get_pressure_unit_str()).units
TIME_UNIT = UREG.parse_expression(bungee.get_time_unit_str()).units
VOLUME_RATE_UNIT = UREG.parse_expression(bungee.get_volume_rate_unit_str()).units

DEPTH_DISPLAY_UNIT = UREG.foot
PRESSURE_DISPLAY_UNIT = UREG.psi
TIME_DISPLAY_UNIT = UREG.minute
VOLUME_RATE_DISPLAY_UNIT = UREG.ft**3 / UREG.minute


def get_plan(path: str):
    with open(path, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    # Water type
    water = getattr(bungee.Water, data["water"])

    # SCR
    working_scr_pint = UREG.parse_expression(data["scr"]["work"]).to(cenote.VOLUME_RATE_UNIT)
    deco_scr_pint = UREG.parse_expression(data["scr"]["deco"]).to(cenote.VOLUME_RATE_UNIT)
    scr = bungee.Scr(
        bungee.VolumeRate(working_scr_pint.m),
        bungee.VolumeRate(deco_scr_pint.m),
    )

    # Tank loadout
    tanks = {}
    for name, info in data["tanks"].items():
        enum = getattr(bungee.Tank, info["type"])
        pressure_pint = UREG.parse_expression(info["pressure"]).to(cenote.PRESSURE_UNIT)
        pressure = bungee.Pressure(pressure_pint.m)
        mix = bungee.Mix(info["mix"]["fO2"])
        tanks[name] = bungee.TankConfig(enum, pressure, mix)

    # Plan
    plan = bungee.Plan(water, scr, tanks)

    # Profile
    for segment_data in data["profile"]:
        if "tank" in segment_data:
            plan.set_tank(segment_data["tank"])
        depth_pint = UREG.parse_expression(segment_data["depth"]).to(cenote.DEPTH_UNIT)
        depth = bungee.Depth(depth_pint.m)
        duration_pint = UREG.parse_expression(segment_data["duration"]).to(cenote.TIME_UNIT)
        duration = bungee.Time(duration_pint.m)
        plan.add_segment(duration, depth)

    plan.finalize()

    return plan


class Result:
    def __init__(self, bungee_result: bungee.Result):
        self.depth = (bungee_result.depth * DEPTH_UNIT).to(DEPTH_DISPLAY_UNIT)
        self.time = (bungee_result.time * TIME_UNIT).to(TIME_DISPLAY_UNIT)
        self.pressure = {
            tank: (pressure * PRESSURE_UNIT).to(PRESSURE_DISPLAY_UNIT)
            for tank, pressure in bungee_result.pressure.items()
        }


def get_result(plan: bungee.Plan):
    bungee_result = bungee.Result(plan)
    return Result(bungee_result)
