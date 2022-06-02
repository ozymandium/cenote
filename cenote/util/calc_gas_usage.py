from cenote import gas_usage as gu
from cenote.config import UREG
from cenote.parse.yaml import parse_dive_from_yaml
from cenote.parse.shearwater_xml import parse_dive_from_shearwater_xml
import argparse
import os
import yaml
import sys


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-y", "--yaml_path", help="Path to YAML file containing dive configuration."
    )
    parser.add_argument("-x", "--shearwater_xml_path", help="Path to Shearwater XML dive log.")
    return parser.parse_args()


def print_dive(dive: gu.Dive):
    print("Profile:")
    for point in dive.profile:
        print("    {}".format(str(point)))
    gas_usage = dive.gas_usage()
    print("Gas usage: {:.2f}".format(gas_usage))


def main():
    args = parse_args()

    if args.yaml_path:
        dive = parse_dive_from_yaml(args.yaml_path)
    elif args.shearwater_xml_path:
        dive = parse_dive_from_shearwater_xml(args.shearwater_xml_path)
    else:
        print("No input file provided.")
        sys.exit(0)
    print_dive(dive)


if __name__ == "__main__":
    main()
