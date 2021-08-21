#!/usr/bin/env python3
from scuba import gas_usage as gu
import argparse
import yaml

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "data_path", help="Path to YAML file containing dive configuration.")
    return parser.parse_args()


def main(args):
    print("Data path: {}".format(args.data_path))

    with open(args.data_path, "r") as f:
        raw_data = yaml.load(f, Loader=yaml.FullLoader)
    
    dive = gu.Dive(raw_data)
    
    print("SAC: {}".format(str(dive.scr)))
    print("Profile:\n    {points}".format(points="\n    ".join([str(p) for p in dive.profile.points])))

    gas_usage = dive.gas_usage()
    print("Gas usage: {:.2f}".format(gas_usage))

if __name__ == "__main__":
    main(parse_args())
