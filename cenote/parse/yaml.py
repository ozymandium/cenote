__all__ = [
    "parse_dive_from_yaml",
    "export_dive_to_yaml",
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


def parse_dive_from_yaml(path: str) -> gu.Plan:
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

    return gu.Plan(profile)


def export_dive_to_yaml(dive: gu.Plan, path: str, scr=None):
    """
    Parameters
    ----------
    dive : cenote.gas_usage.Dive
    path : str
        Path to YAML file to write
    scr : cenote.gas_usage.Scr (optional)
        Default SCR for the whole dive, to use in sections with no specific SCR. Will not be written
        if not provided.
    """
    data = {}

    # SCR
    if scr is not None:
        data["scr"] = str(scr)

    # Profile
    data["profile"] = [_point_to_dict(point) for point in dive.points]

    with open(path, "w") as f:
        yaml.dump(data, f)
