#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path

from llama.extractors.herbarium_extractor import DWC


def main(args: argparse.Namespace) -> None:
    match args.oopsie:
        case "fix-duplicate-annotations":
            fix_duplicate_annotations(args)
        case "fix-annotation-struct":
            fix_annotation_struct(args)
        case "rebuild-label-outlines":
            rebuild_label_outlines(args)


def rebuild_label_outlines(args: argparse.Namespace) -> None:
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


def fix_duplicate_annotations(args: argparse.Namespace) -> None:
    with args.bad_annotations.open() as f:
        bad = json.load(f)

    fixed = []
    for lb in bad:
        good = {
            "Source-File": lb["Source-File"],
            "text": lb["text"],
            "annotations": {v: [] for v in DWC.values()},
        }
        for key, values in lb["annotations"].items():
            for val in values:
                if val not in good["annotations"][key]:
                    good["annotations"][key].append(val)
        fixed.append(good)

    with args.good_annotations.open("w") as f:
        json.dump(fixed, f, indent=4)


def fix_annotation_struct(args: argparse.Namespace) -> None:
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
                good["annotations"][key].append(val)
        fixed.append(good)

    with args.good_annotations.open("w") as f:
        json.dump(fixed, f, indent=4)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
            Fix mistakes or alter data.

            rebuild-label-outlines: I accidentally deleted the label outline JSON file.
                This utility recreates it from the labels themselves and the sheet
                directory. Args: --sheet-dir, --label-dir, --outline-json

            fix-duplicate-annotations: There was an issue where multiple copies of
                values were in each field. Args: --bad-annotations, --good-annotations

            fix-annotation-struct: I originally had annotations at the top level of the
                output JSON file. I later wanted to nest them under the "annotations"
                dict. Args: --bad-annotations, --good-annotations
            """
        ),
    )

    arg_parser.add_argument(
        "--oopsie",
        choices=[
            "rebuild-label-outlines",
            "fix-duplicate-annotations",
            "fix-annotation-struct",
        ],
        required=True,
        help="""What are you fixing/changing.""",
    )

    arg_parser.add_argument(
        "--sheet-dir",
        type=Path,
        metavar="PATH",
        help="""The directory containing the herbarium sheet images.""",
    )

    arg_parser.add_argument(
        "--label-dir",
        type=Path,
        metavar="PATH",
        help="""Get label images from this directory.""",
    )

    arg_parser.add_argument(
        "--outline-json",
        type=Path,
        metavar="PATH",
        help="""Output the label outlines to this JSON file.""",
    )

    arg_parser.add_argument(
        "--bad-annotations",
        type=Path,
        metavar="PATH",
        help="""The JSON file with bad annotations.""",
    )

    arg_parser.add_argument(
        "--good-annotations",
        type=Path,
        metavar="PATH",
        help="""Save fixed annotations to this JSON file.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
