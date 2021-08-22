#!/usr/bin/env python3
from cenote import gas_usage as gu
from cenote.config import UREG
import argparse
import os
import yaml


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path", help="Path to YAML file containing dive configuration.")
    return parser.parse_args()


def parse_dive(data: dict):
    # SCR
    volume_rate = UREG.parse_expression(data["scr"])
    scr = gu.Scr(volume_rate)

    # Profile
    points = []
    for point_data in data["profile"]:
        time = UREG.parse_expression(point_data["time"])
        depth = UREG.parse_expression(point_data["depth"])
        point = gu.ProfilePoint(time, depth)
        points.append(point)
    profile = gu.Profile(points)

    return gu.Dive(scr, profile)


def print_dive(dive: gu.Dive):
    print("SCR: {}".format(str(dive.scr)))
    print("Profile:")
    for point in dive.profile.points:
        print("    {}".format(str(point)))
    gas_usage = dive.gas_usage()
    print("Gas usage: {:.2f}".format(gas_usage))


def main(args):
    data_path = os.path.abspath(args.data_path)
    print("YAML path: {}".format(data_path))
    with open(args.data_path, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    dive = parse_dive(data)
    print_dive(dive)


if __name__ == "__main__":
    main(parse_args())
