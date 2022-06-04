from cenote import gas_usage as gu
from cenote.config import UREG
import pint
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--scr",
        required=True,
        help="Surface Consumption Rate in volume per time (eg 15L/min).",
    )
    parser.add_argument(
        "-t", "--tank", required=True, choices=gu.TANKS, help="Name of tank (from list)"
    )
    parser.add_argument(
        "-u", "--units", help="What units to output the SAC in (eg psi/min, or bar/hr)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # parse inputs
    volume_rate = UREG.parse_expression(args.scr)
    tank = gu.TANKS[args.tank]
    units = UREG.parse_expression(args.units) if args.units else None

    # create objects
    scr = gu.Scr(volume_rate)
    sac = scr.sac(tank)

    # convert if desired
    if units:
        sac = sac.to(units)

    # output
    print("{:.2f}".format(sac))
