__all__ = [
    "parse_plan_from_yaml",
    "export_plan_to_yaml",
]

from cenote import gas_usage as gu
from cenote.config import UREG
import yaml

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

    # Profile
    profile = []
    for point_data in data["profile"]:
        time = UREG.parse_expression(point_data["time"])
        depth = UREG.parse_expression(point_data["depth"])
        if "scr" in point_data:
            volume_rate = UREG.parse_expression(point_data["scr"])
            scr = gu.Scr(volume_rate)
        else:
            scr = default_scr
        point = gu.PlanPoint(time, depth, scr)
        profile.append(point)

    return gu.Plan(profile, water)


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
