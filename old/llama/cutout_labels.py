#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image
from tqdm import tqdm


def main(args: argparse.Namespace) -> None:
    args.label_dir.mkdir(parents=True, exist_ok=True)

    with args.sheet_labels.open() as f:
        sheets = json.load(f)

    for sheet in tqdm(sheets):
        path = Path(sheet["path"])
        stem = path.stem
        suffix = path.suffix
        with Image.open(path) as image:
            for box in sheet["boxes"]:
                x0 = box["x0"]
                y0 = box["y0"]
                x1 = box["x1"]
                y1 = box["y1"]
                content = box["content"]
                name = f"{stem}_{content}_{x0}_{y0}_{x1}_{y1}{suffix}"
                box_path = args.label_dir / name
                cropped = image.crop((x0, y0, x1, y1))
                cropped.save(box_path)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Cut marked labels out of herbarium sheets."""),
    )

    arg_parser.add_argument(
        "--sheet-labels",
        type=Path,
        required=True,
        metavar="PATH",
        help="""JSON file containing marked labels on sheets.""",
    )

    arg_parser.add_argument(
        "--label-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Put label images into this directory.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
