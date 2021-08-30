"""
Parse a Shearwater XML dive log as output from the Shearwater
"""
from cenote import gas_usage as gu
from cenote import config
import xml.etree.ElementTree as ET
import ipdb
import functools
import sys


UREG = config.UREG
DIVE_TIME_UNIT = UREG.millisecond
IMPERIAL_DEPTH_UNIT = UREG.foot
IMPERIAL_PRESSURE_RATE_UNIT = UREG.psi / UREG.minute


def debug(*exceptions):
    if not exceptions:
        exceptions = (Exception,)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as exc:
                print("--- Error: ---\n{}\n--------------".format(exc))
                ipdb.post_mortem(sys.exc_info()[2])

        return wrapper

    return decorator


@debug()
def parse_dive_from_shearwater_xml(path: str, tank: gu.Tank):
    """
    Parses an XML file output from Shearwater Cloud application.

    Parameters
    ----------
    path : str
        Absolute path to XML file.

    Returns
    -------
    cenote.gas_usage.Dive
    """
    et = ET.parse(path)
    log = et.find("diveLog")

    # what units are we using?
    use_imperial_units_str = log.find("imperialUnits").text
    if use_imperial_units_str == "false":
        use_imperial_units = False
    elif use_imperial_units_str == "true":
        use_imperial_units = True
    else:
        raise Exception("I don't actually know what all the values of imperialUnits are...")
    if use_imperial_units:
        depth_unit = IMPERIAL_DEPTH_UNIT
        pressure_rate_unit = IMPERIAL_PRESSURE_RATE_UNIT
    else:
        raise NotImplementedError("metric measurements not yet supported")

    # get individual samples
    profile = []
    records = log.find("diveLogRecords")
    for record in records.iterfind("diveLogRecord"):
        time_xml = record.find("currentTime")
        depth_xml = record.find("currentDepth")
        pressure_rate_xml = record.find("sac").text
        assert time_xml is not None
        assert depth_xml is not None
        assert pressure_rate_xml is not None
        time = int(time_xml.text) * DIVE_TIME_UNIT
        depth = float(depth_xml.text) * depth_unit
        try:
            pressure_rate = float(pressure_rate_xml) * pressure_rate_unit
            scr = gu.Scr.from_sac(pressure_rate, tank)
        except:
            scr = None
        point = gu.ProfilePoint(time, depth, scr=scr)
        profile.append(point)

    return gu.Dive(profile)
