__all__ = [
    "parse_plan_from_yaml",
    "export_plan_to_yaml",
]

from cenote import gas_usage as gu
from cenote import tank
from cenote import config

import yaml


UREG = config.UREG


#
# Private Utility Functions
#


def _point_to_dict(point: gu.PlanPoint) -> dict:
    d = {
        "time": str(point.time),
        "depth": str(point.depth),
    }
    if point.scr is not None:
        d["scr"]: str(point.scr)
    return d


#
# Public Functions
#


def parse_plan_from_yaml(path: str) -> gu.Plan:
    """
    Parameters
    ----------
    path : str
        Path to YAML file with dive plan.

    Returns
    -------
    cenote.gas_usage.Dive
    """
    # Read YAML
    with open(path, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    # water type
    water = gu.Water[data["water"]]

    # SCR
    default_volume_rate = UREG.parse_expression(data["scr"])
    default_scr = gu.Scr(default_volume_rate)

    # tank info
    tank_info = {}
    for entry in data["tanks"]:
        name = entry["name"]
        enum = tank.Tank[entry["type"]]
        pressure = UREG.parse_expression(entry["pressure"])
        tank_info[name] = gu.TankInfo(enum, pressure)

    plan = gu.Plan(water, default_scr, tank_info)

    # Profile
    for point_data in data["profile"]:
        kwargs = {}
        # optional SCR
        if "scr" in point_data:
            volume_rate = UREG.parse_expression(point_data["scr"])
            kwargs["scr"] = gu.Scr(volume_rate)
        # optional tank name
        if "tank" in point_data:
            kwargs["tank_name"] = point_data["tank"]

        if len(plan.points) == 0:
            # this is the first point. set depth and time to zero
            time = 0 * config.TIME_UNIT
            depth = 0 * config.DEPTH_UNIT
            if "tank_name" not in kwargs:
                raise Exception("First entry in profile must contain tank")
            plan.add_point(time, depth, **kwargs)

        duration = UREG.parse_expression(point_data["duration"])
        time = plan.back().time + duration

        depth = UREG.parse_expression(point_data["depth"])

        plan.add_point(time, depth, **kwargs)

    return plan


def export_plan_to_yaml(plan: gu.Plan, path: str, scr=None):
    """
    Parameters
    ----------
    plan : cenote.gas_usage.Dive
    path : str
        Path to YAML file to write
    scr : cenote.gas_usage.Scr (optional)
        Default SCR for the whole plan, to use in sections with no specific SCR. Will not be written
        if not provided.
    """
    data = {}

    # water
    data["water"] = plan.water.name

    # SCR
    data["scr"] = str(scr)

    # Profile
    data["profile"] = [_point_to_dict(point) for point in plan.points]

    with open(path, "w") as f:
        yaml.dump(data, f)
