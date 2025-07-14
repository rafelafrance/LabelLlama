#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path


def main(args):
    sheets = {
        p.stem: {"path": str(p.absolute()), "boxes": []}
        for p in sorted(args.sheet_dir.glob("*.jpg"))
    }

    for label in sorted(args.label_dir.glob("*.jpg")):
        *key, content, x0, y0, x1, y1 = label.stem.split("_")
        key = "_".join(key)
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        sheets[key]["boxes"].append(
            {"x0": x0, "y0": y0, "x1": x1, "y1": y1, "content": content}
        )

    with args.outline_json.open("w") as f:
        json.dump(list(sheets.values()), f, indent=4)


def parse_args():
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
        Rebuild the outline_labels JSON output file.

        I accidentally deleted the label outline JSON file. This utility recreates it
        from the labels themselves and the sheet directory.
        """
        ),
    )

    arg_parser.add_argument(
        "--sheet-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""The directory containing the herbarium sheet images.""",
    )

    arg_parser.add_argument(
        "--label-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Get label images from this directory.""",
    )

    arg_parser.add_argument(
        "--outline-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output the label outlines to this JSON file.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
