#!/usr/bin/env python3
from colorspacious import cspace_convert
import numpy as np
import sys


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a color font with ligatures.")
    parser.add_argument("input", help="Path to the input font file")
    parser.add_argument("--l-from", help="Luminance range to map from", type=float, nargs=2, default=[0.0, 1.0])
    parser.add_argument("--l-to", help="Luminance range to map to", type=float, nargs=2, default=[0.0, 1.0])
    args = parser.parse_args()

    k = (args.l_to[1] - args.l_to[0]) / (args.l_from[1] - args.l_from[0])
    b = (args.l_to[0] - k * args.l_from[0]) * 100.0
    with open(args.input) as f:
        for line in f:
            color, *etc = line.rstrip("\t\r\n").split("\t")
            color = color.lstrip("#")
            rgb = [int(color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
            lab = cspace_convert(rgb, "sRGB1", "CIELab")
            if lab[0] < args.l_from[0] * 100.0 or lab[0] > args.l_from[1] * 100.0:
                print(f"L {lab[0]/100.0:.2f} out of source range for {color}", file=sys.stderr)
            lab[0] = lab[0] * k + b
            if not (0 <= lab[0] <= 100):
                print(f"L {lab[0]/100.0:.2f} out of bounds for {color}, truncated.", file=sys.stderr)
                lab[0] = np.clip(lab[0], 0, 100)
            rgb = cspace_convert(lab, "CIELab", "sRGB1")
            rgb = [int(round(np.clip(c, 0, 1) * 255)) for c in rgb]
            print('#{:02X}{:02X}{:02X}'.format(*rgb) + "\t" + "\t".join(etc))
