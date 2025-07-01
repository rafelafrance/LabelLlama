#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path


def main(args):
    args.text_dir.mkdir(parents=True, exist_ok=True)

    with args.ocr_jsonl.open() as f:
        labels = [json.loads(ln) for ln in f]

    for lb in labels:
        source = Path(lb["Source-File"]).stem
        dst = args.text_dir / f"{source}.txt"
        with dst.open("w") as f:
            f.write(lb["text"])


def parse_args():
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Cut marked labels out of herbarium sheets."""),
    )

    arg_parser.add_argument(
        "--ocr-jsonl",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Get OCR results from this JSONL file.""",
    )

    arg_parser.add_argument(
        "--text-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Put OCRed text of labels into this directory.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
