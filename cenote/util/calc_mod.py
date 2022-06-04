from cenote.tank import Mix
from cenote.water import Water

import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mix_po2",
        type=float,
        help="Portion of oxygen (0.0-1.0). Or: the partial pressure of oxygen in the mix as measured in ATA at sea level.",
    )
    parser.add_argument(
        "max_po2", type=float, help="Max partial pressure of oxygen in ATA."
    )
    parser.add_argument("water", type=lambda w: Water[w], choices=list(Water), help="Type of water.")
    return parser.parse_args()


def main():
    args = parse_args()

    mix = Mix(po2=args.mix_po2, phe=0.0)
    mod = mix.mod(args.max_po2, args.water)

    print("{:.1f}".format(mod))
