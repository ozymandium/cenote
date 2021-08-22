#!/usr/bin/env python3
from scuba import gas_usage as gu
import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path", help="Path to YAML file containing dive configuration.")
    return parser.parse_args()


def main(args):
    data_path = os.path.abspath(args.data_path)
    print("YAML path: {}".format(data_path))

    dive = gu.Dive.from_yaml(data_path)

    print("SCR: {}".format(str(dive.scr)))
    print("Profile:")
    for point in dive.profile.points:
        print("    {}".format(str(point)))

    gas_usage = dive.gas_usage()
    print("Gas usage: {:.2f}".format(gas_usage))


if __name__ == "__main__":
    main(parse_args())
