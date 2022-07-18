import cenote.units
import bungee
import pint
import yaml


UREG = cenote.units.UREG


def get_plan(path: str):
    with open(path, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    # water type
    water = getattr(bungee.Water, data["water"])

    # SCR
    working_scr_pint = UREG.parse_expression(data["scr"]["work"]).to(cenote.units.VOLUME_RATE_UNIT)
    deco_scr_pint = UREG.parse_expression(data["scr"]["deco"]).to(cenote.units.VOLUME_RATE_UNIT)
    scr = bungee.Scr(
        bungee.VolumeRate(working_scr_pint.m),
        bungee.VolumeRate(deco_scr_pint.m),
    )

    # Tank loadout
    tanks = {}
    for name, info in data["tanks"].items():
        enum = getattr(bungee.Tank, info["type"])
        pressure_pint = UREG.parse_expression(info["pressure"]).to(cenote.units.PRESSURE_UNIT)
        pressure = bungee.Pressure(pressure_pint.m)
        mix = bungee.Mix(info["mix"]["fO2"])
        tanks[name] = bungee.TankConfig(enum, pressure, mix)
        
    # Plan
    plan = bungee.Plan(water, scr, tanks)

    # Profile
    for segment_data in data["profile"]:
        if "tank" in segment_data:
            plan.set_tank(segment_data["tank"])
        depth_pint = UREG.parse_expression(segment_data["depth"]).to(cenote.units.DEPTH_UNIT)
        depth = bungee.Depth(depth_pint.m)
        duration_pint = UREG.parse_expression(segment_data["duration"]).to(cenote.units.TIME_UNIT)
        duration = bungee.Time(duration_pint.m)
        plan.add_segment(duration, depth)

    return plan