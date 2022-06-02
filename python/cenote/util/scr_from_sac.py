from cenote import gas_usage as gu
from cenote.config import UREG
import pint
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--sac",
        required=True,
        help="Surface Air Consumption: rate of pressure drop in tank (eg 20psi/min).",
    )
    parser.add_argument("-t", "--tank", required=True, choices=gu.TANKS, help="Name of tank (from list)")
    parser.add_argument(
        "-u", "--units", help="What units to output the SAC in (eg L/min, or cm**3/s)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # parse inputs
    pressure_rate = UREG.parse_expression(args.sac)
    tank = gu.TANKS[args.tank]
    units = UREG.parse_expression(args.units) if args.units else None

    # create objects
    scr = gu.Scr.from_sac(pressure_rate, tank)
    volume_rate = scr.volume_rate

    # convert to output units if requested
    if units:
        volume_rate = volume_rate.to(units)

    # output
    print("{:.2f}".format(volume_rate))


if __name__ == "__main__":
    main()
