from cenote.parse.shearwater_xml import (
    parse_dive_from_shearwater_xml,
    ScrSource
)
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
    parser.add_argument("--scr_source", choices=["REPORTED", "PRESSURE", "NONE"], default="NONE")
    return parser.parse_args()


def main(args):
    args = parse_args()

    tank = gu.Tank(
        UREG.parse_expression(args.tank_max_gas_volume),
        UREG.parse_expression(args.tank_max_pressure),
    )
    
    scr_source = ScrSource[args.scr_source]
    dive = parse_dive_from_shearwater_xml(args.xml_path, tank, scr_source)
    export_dive_to_yaml(dive, args.yaml_path, scr=scr)


if __name__ == "__main__":
    main()
