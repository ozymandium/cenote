#!/usr/bin/env python3
from cenote import gas_usage as gu
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
    parser.add_argument(
        "-v",
        "--volume",
        required=True,
        help="Volume of 1atm air that the tank holds (eg 80ft**3 for an AL80)",
    )
    parser.add_argument(
        "-p", "--pressure", required=True, help="Maximum rated pressure of the tank (eg 3000psi)"
    )
    parser.add_argument(
        "-u", "--units", help="What units to output the SAC in (eg L/min, or cm**3/s)"
    )
    return parser.parse_args()


def main(args):
    # parse inputs
    ureg = pint.UnitRegistry()
    pressure_rate = ureg.parse_expression(args.sac)
    max_gas_volume = ureg.parse_expression(args.volume)
    max_pressure = ureg.parse_expression(args.pressure)
    units = ureg.parse_expression(args.units) if args.units else None

    # create objects
    tank = gu.Tank(max_gas_volume, max_pressure)
    sac = gu.Sac(pressure_rate, tank)
    volume_rate = sac.scr.volume_rate

    # convert to output units if requested
    if units:
        volume_rate = volume_rate.to(units)

    # output
    print("{:.2f}".format(volume_rate))


if __name__ == "__main__":
    main(parse_args())
