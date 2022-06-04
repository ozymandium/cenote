__all__ = [
    "parse_plan_from_yaml",
    "export_plan_to_yaml",
]

from cenote import gas_usage as gu
from cenote import tank
from cenote import config
from cenote import mix

import yaml
import numpy as np


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
        mix = mix.Mix(po2=entry["mix"]["po2"])
        tank_info[name] = gu.TankInfo(enum, pressure, mix)

    plan = gu.Plan(water, default_scr, tank_info)

    # get a list of times in minutes
    durations = [
        UREG.parse_expression(p["duration"]).to(config.TIME_UNIT).magnitude for p in data["profile"]
    ]
    times = [float(d) * config.TIME_UNIT for d in np.cumsum([0.0] + durations)]

    # get a list of depths
    depths = [0 * config.DEPTH_UNIT] + [UREG.parse_expression(p["depth"]) for p in data["profile"]]

    # scr points
    scrs = [
        gu.Scr(UREG.parse_expression(p["scr"])) if "scr" in p else None for p in data["profile"]
    ] + [None]

    # tank points
    tanks = [p["tank"] if "tank" in p else None for p in data["profile"]]
    tanks += [tanks[-1]]
    if tanks[0] is None:
        raise Exception("First entry in profile must contain tank")

    N = len(times)
    assert len(depths) == N
    assert len(scrs) == N
    assert len(tanks) == N
    for i in range(N):
        plan.add_point(time=times[i], depth=depths[i], scr=scrs[i], tank_name=tanks[i])

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
