#!/usr/bin/env python3
import argparse

import bungee
import cenote

import numpy as np
import tabulate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", action="append", type=str, required=True)
    parser.add_argument("-t", "--tank", action="append", type=str, choices=bungee.TankType.__members__.keys(), required=True)
    parser.add_argument("-p", "--pressure", action="append", type=int, required=True)
    parser.add_argument("-f", "--turn", type=int, default=3, help="fraction to turn at (thirds -> `3`)")
    parser.add_argument("--pressure-unit", type=str, default="psi", choices=("psi", "bar"), help="pressure units")
    parser.add_argument("--volume-unit", type=str, default="ft**3", choices=("ft**3", "liter"), help="volume units")
    args = parser.parse_args()
    if len(args.name) != len(args.tank) or len(args.tank) != len(args.pressure):
        raise Exception("must pass same number of each argument `name`, `tank`, `pressure")
    return args


def main(args: argparse.Namespace) -> None:
    print(f"\nDive To:            1/{args.turn}")

    pressure_unit = cenote.UREG.parse_units(args.pressure_unit)
    volume_unit = cenote.UREG.parse_units(args.volume_unit)
    
    # handle input args
    names = [name for name in args.name]
    tank_types = [getattr(bungee.TankType, tank) for tank in args.tank]
    # pint quantity in user unit
    start_pressures_pint = [pressure * pressure_unit for pressure in args.pressure]

    # pybind quantity in internal unit
    start_pressures = [
        bungee.Pressure((pressure).to(cenote.PRESSURE_UNIT).m)
        for pressure in start_pressures_pint
    ]
    tanks = list(map(bungee.get_tank_at_pressure, tank_types, start_pressures))
    start_volumes = np.array([t.volume.value for t in tanks])

    controlling_diver = np.argmin(start_volumes)
    print(f"Controlling Diver:  {names[controlling_diver]}")
    # if len(controlling_diver) > 1:
    #     # have to handle case where controlling diver has different type tank than other 
    #     # controlling diver
    #     raise Exception("more than 1 controlling diver is not handled")
    usable_volume = start_volumes[controlling_diver] / float(args.turn)
    turn_volumes = start_volumes - usable_volume
    turn_pressures = [t.pressure_at_volume(bungee.Volume(v)) for t, v in zip(tanks, turn_volumes)]    

    # pint quantity in user unit
    print(f"Usable Gas:         {(usable_volume * cenote.VOLUME_UNIT).to(volume_unit):~.1f}")
    start_volumes_pint = (start_volumes * cenote.VOLUME_UNIT).to(volume_unit)
    turn_volumes_pint = (turn_volumes * cenote.VOLUME_UNIT).to(args.volume_unit)
    turn_pressures_pint = [
        (p.value * cenote.PRESSURE_UNIT).to(pressure_unit)
        for p in turn_pressures
    ]

    tbl = tabulate.tabulate(
        np.array([
            names,
            [t.name for t in tank_types],
            [f"{p:.0~f}" for p in start_pressures_pint],
            [f"{v:.0~f}" for v in start_volumes_pint],
            [f"{p:.0~f}" for p in turn_pressures_pint],
            [f"{v:.0~f}" for v in turn_volumes_pint],
        ]).transpose().tolist(),
        headers = ["Diver", "Tank", "Start Press", "Start Volume", "Turn Press", "Turn Volume"],
        showindex=False,
        numalign="right",
        stralign="left",
        floatfmt=".0P~",
        tablefmt="fancy_grid",
    )
    print(tbl)


if __name__ == "__main__":
    main(parse_args())
