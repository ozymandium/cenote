"""
Parse a Shearwater XML dive log as output from the Shearwater
"""
from cenote import gas_usage as gu
from cenote.tank import TankBase
from cenote import config
import xml.etree.ElementTree as ET
import ipdb
import functools
import sys
import enum


UREG = config.UREG
DIVE_TIME_UNIT = UREG.millisecond
IMPERIAL_DEPTH_UNIT = UREG.foot
IMPERIAL_PRESSURE_RATE_UNIT = UREG.psi / UREG.minute
IMPERIAL_PRESSURE_UNIT = UREG.psi


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


def get_time_from_record(record):
    time_xml = record.find("currentTime")
    assert time_xml is not None
    return int(time_xml.text) * DIVE_TIME_UNIT


def get_depth_from_record(record):
    depth_xml = record.find("currentDepth")
    assert depth_xml is not None
    return float(depth_xml.text) * depth_unit


# def get_pressure_rate_from_record(record):
class ScrSource(enum.Enum):
    NONE = enum.auto()
    REPORTED = enum.auto()
    PRESSURE = enum.auto()


@debug()
def parse_dive_from_shearwater_xml(path: str, tank: TankBase):
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
        pressure_unit = IMPERIAL_PRESSURE_UNIT
    else:
        raise NotImplementedError("metric measurements not yet supported")

    # get individual samples
    profile = []
    records = log.find("diveLogRecords")
    for record in records.iterfind("diveLogRecord"):
        # time
        time = get_time_from_record(record)
        # depth
        depth = get_depth_from_record(record)

        # pressure rate if doing scr from reported sac
        pressure_rate_xml = record.find("sac")
        assert pressure_rate_xml is not None
        try:
            pressure_rate = float(pressure_rate_xml.text) * pressure_rate_unit
            scr = gu.Scr.from_sac(pressure_rate, tank)
        except:
            scr = None

        # pressure if doing scr from change in pressure
        pressure_xml = record.find("tank0pressurePSI")
        assert pressure_xml is not None
        pressure = float(pressure_xml.text) * pressure_unit

        # make the point
        point = gu.ProfilePoint(time, depth, scr=scr)
        profile.append(point)

    # now return and back-fill default scrs for points with no scr
    if scr_source is ScrSource.REPORTED:
        # find first non-none scr as the default
        for point in dive.profile:
            if point.scr is not None:
                print("Using first SCR as default: {}".format(point.scr))
                scr = point.scr
                break
        if scr is None:
            print("Warning: Requested using first SCR as default, but SCR was never found.")
    elif scr_source is ScrSource.PRESSURE:
        raise NotImplementedError

    return gu.Dive(profile)
