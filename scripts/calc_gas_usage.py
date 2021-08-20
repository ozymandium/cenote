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
        raw_data = yaml.load(f)
    
    dive = gu.Dive(raw_data)
    
    print("SAC:\n{}\n".format(str(dive.sac)))
    print("Profile:\n{points}\n".format(points="\n".join([str(p) for p in dive.profile.points])))


if __name__ == "__main__":
    main(parse_args())
