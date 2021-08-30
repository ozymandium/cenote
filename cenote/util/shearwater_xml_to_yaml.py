#!/usr/bin/env python3
from cenote.parse.shearwater_xml import parse_dive_from_shearwater_xml
from cenote.parse.yaml import export_dive_to_yaml
from cenote.config import UREG
from cenote import gas_usage as gu
import argparse
import yaml


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("xml_path")
    parser.add_argument("yaml_path")
    parser.add_argument("-v", "--tank_max_gas_volume", required=True)
    parser.add_argument("-p", "--tank_max_pressure", required=True)
    parser.add_argument("--use_first_scr_as_default", action="store_true")
    return parser.parse_args()


def main(args):
    tank = gu.Tank(
        UREG.parse_expression(args.tank_max_gas_volume),
        UREG.parse_expression(args.tank_max_pressure),
    )
    dive = parse_dive_from_shearwater_xml(args.xml_path, tank)

    scr = None
    if args.use_first_scr_as_default:
        # find first non-none scr as the default
        for point in dive.profile:
            if point.scr is not None:
                print("Using first SCR as default: {}".format(point.scr))
                scr = point.scr
                break
        if scr is None:
            print("Warning: Requested using first SCR as default, but SCR was never found.")

    export_dive_to_yaml(dive, args.yaml_path, scr=scr)


if __name__ == "__main__":
    main(parse_args())
