#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path


def main(args: argparse.Namespace) -> None:
    match args.oopsie:
        case "move-images":
            move_images(args)
        case "rebuild-json":
            rebuild_json(args)


def rebuild_json(args: argparse.Namespace) -> None:
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


def move_images(args: argparse.Namespace) -> None:
    with args.outline_json.open() as f:
        sheets = json.load(f)

    for sheet in sheets:
        old = Path(sheet["path"])
        new = args.sheet_dir / old.name
        sheet["path"] = str(new)

    with args.outline_json.open("w") as f:
        json.dump(sheets, f, indent=4)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
            Edit data in the outline labels JSON file.

            Backup the outline JSON file you're going to edit first.

            move-images: Change the file paths to where you moved the herbarium sheets.
                Required args: --outline-json, --sheet-dir

            rebuild-json: I accidentally deleted the label outline JSON file.
                This utility recreates it from the labels themselves and the sheet
                directory. Required args: --outline-json, --sheet-dir, --label-dir
            """
        ),
    )

    arg_parser.add_argument(
        "--oopsie",
        choices=[
            "move-images",
            "rebuild-json",
        ],
        required=True,
        help="""What are you fixing/changing.""",
    )

    arg_parser.add_argument(
        "--outline-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Edit this JSON file.""",
    )

    arg_parser.add_argument(
        "--sheet-dir",
        type=Path,
        metavar="PATH",
        help="""Change the directory containing the herbarium sheet images to this.
            You moved the herbarium sheet images.""",
    )

    arg_parser.add_argument(
        "--label-dir",
        type=Path,
        metavar="PATH",
        help="""When rebuilding an outline JSON file get label images from this
            directory. You deleted the outline JSON file.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
