from cenote import gas_usage as gu
from cenote.config import UREG
from cenote.parse.yaml import parse_plan_from_yaml
from cenote.parse.shearwater_xml import parse_dive_from_shearwater_xml
from cenote.util import plot
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


def print_plan(plan: gu.Plan, result: gu.Result):
    print("Profile:")
    for point in plan.points:
        print("    {}".format(str(point)))
    print("Gas usage: {:.2f}".format(result.consumed_volume()))


def main():
    args = parse_args()

    if args.yaml_path:
        plan = parse_plan_from_yaml(args.yaml_path)
    elif args.shearwater_xml_path:
        plan = parse_dive_from_shearwater_xml(args.shearwater_xml_path)
    else:
        print("No input file provided.")
        sys.exit(0)

    result = gu.Result(plan)

    print_plan(plan, result)
    plot.plot(plan, result)


if __name__ == "__main__":
    main()
