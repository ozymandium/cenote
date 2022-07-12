from cenote.usage import Plan, Scr, TankInfo
from cenote.tank import Tank
from cenote import config
from cenote.mix import Mix
from cenote.water import Water
from cenote.deco import BuhlmannParams

import yaml
import numpy as np


UREG = config.UREG


def plan_from_yaml(path: str) -> Plan:
    """
    Parameters
    ----------
    path : str
        Path to YAML file with dive plan.

    Returns
    -------
    Plan
    """
    # Read YAML
    with open(path, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    # water type
    water = Water[data["water"]]

    # SCR
    default_volume_rate = UREG.parse_expression(data["scr"])
    default_scr = Scr(default_volume_rate)

    # tank info
    tank_info = {}
    for entry in data["tanks"]:
        name = entry["name"]
        enum = Tank[entry["type"]]
        pressure = UREG.parse_expression(entry["pressure"])
        mix = Mix(po2=entry["mix"]["po2"])
        tank_info[name] = TankInfo(enum, pressure, mix)

    # decompression
    deco = BuhlmannParams(gf_low=data["deco"]["gf_low"], gf_high=data["deco"]["gf_high"])

    # create the plan object
    plan = Plan(water, default_scr, tank_info, deco)

    ## profile
    # get a list of times in minutes
    durations = [
        UREG.parse_expression(p["duration"]).to(config.TIME_UNIT).magnitude for p in data["profile"]
    ]
    times = [float(d) * config.TIME_UNIT for d in np.cumsum([0.0] + durations)]
    # get a list of depths
    depths = [0 * config.DEPTH_UNIT] + [UREG.parse_expression(p["depth"]) for p in data["profile"]]
    # scr points
    scrs = [
        Scr(UREG.parse_expression(p["scr"])) if "scr" in p else None for p in data["profile"]
    ] + [None]
    # tank points
    tanks = [p["tank"] if "tank" in p else None for p in data["profile"]]
    tanks += [tanks[-1]]
    if tanks[0] is None:
        raise Exception("First entry in profile must contain tank")

    N = len(times)

    # other checks
    assert len(depths) == N
    assert len(scrs) == N
    assert len(tanks) == N

    # populate the profile points
    for i in range(N):
        plan.add_point(time=times[i], depth=depths[i], scr=scrs[i], tank_name=tanks[i])

    plan.validate()

    return plan
