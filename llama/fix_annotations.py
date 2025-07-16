#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path

from pylib.darwin_core import DWC


def main(args):
    with args.bad_annotations.open() as f:
        bad = json.load(f)

    fixed = []
    for lb in bad:
        good = {
            "Source-File": lb["Source-File"],
            "text": lb["text"],
            "annotations": {v: [] for v in DWC.values()},
        }
        for key, values in lb.items():
            if key in ("Source-File", "text"):
                continue
            for val in values:
                if val not in good["annotations"].get(key):
                    good["annotations"][key].append(val)
        fixed.append(good)

    with args.annotations_json.open("w") as f:
        json.dump(fixed, f, indent=4)


def parse_args():
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
        Fix annotation fields.

        A bug in the annotate fields script caused annotations to be save with an
        improper structure. This utility fixes it.
        """
        ),
    )

    arg_parser.add_argument(
        "--bad-annotations",
        type=Path,
        required=True,
        metavar="PATH",
        help="""The JSON file with bad annotations.""",
    )

    arg_parser.add_argument(
        "--annotations-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Save fixed annotations to this JSON fiel.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
