#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path


def main(args: argparse.Namespace) -> None:
    with args.annotation_json.open() as f:
        labels = json.load(f)

    for lb in labels:
        if args.label_dir:
            old = Path(lb["Source-File"])
            new = args.label_dir / old.name
            lb["Source-File"] = str(new)

        if args.add:
            for field in args.add:
                lb["annotations"][field] = []

        if args.delete:
            for field in args.delete:
                del lb["annotations"][field]

    with args.annotation_json.open("w") as f:
        json.dump(labels, f, indent=4)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
            Edit data in the label annotations JSON file.

            Backup the label annotations JSON file you're going to edit first.
            """
        ),
    )

    arg_parser.add_argument(
        "--annotation-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Edit this JSON file.""",
    )

    arg_parser.add_argument(
        "--add",
        action="append",
        metavar="FIELD",
        help="""Add this field to the annotations. You may uses this more than once.""",
    )

    arg_parser.add_argument(
        "--delete",
        action="append",
        metavar="FIELD",
        help="""Delete this field from the annotations. You may uses this more
            than once.""",
    )

    arg_parser.add_argument(
        "--label-dir",
        type=Path,
        metavar="PATH",
        help="""Update the herbarium label images directory to this.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
