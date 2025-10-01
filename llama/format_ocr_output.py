#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path
from typing import Any

from llama.data_formats import label_types


def main(args: argparse.Namespace) -> None:
    labels = []

    match args.ocr_engine:
        case "olmocr":
            labels = olmocr_output(args.ocr_results)

    label_type = label_types.LABEL_TYPES[args.label_type]
    for lb in labels:
        lb["annotations"] = {k: [] for k in label_type.output_fields}

    with args.annotation_json.open("w") as f:
        json.dump(labels, f, indent=4)


def olmocr_output(ocr_results: Path) -> list[dict[str, Any]]:
    with ocr_results.open() as f:
        ocr = [json.loads(ln) for ln in f]

    return [{"path": lb["metadata"]["Source-File"], "text": lb["text"]} for lb in ocr]


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Format output from an OCR engine for the Label Llama pipeline."""
        ),
    )

    arg_parser.add_argument(
        "--ocr-engine",
        choices=["olmocr"],
        default="olmocr",
        metavar="OCR",
        help="""The data is in what OCR format.""",
    )

    arg_parser.add_argument(
        "--ocr-results",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Read this file containing OCR results. OlmOCR is a JSONL file.""",
    )

    choices = list(label_types.LABEL_TYPES.keys())
    arg_parser.add_argument(
        "--label-type",
        choices=choices,
        default=choices[0],
        help="""Use this label model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--annotation-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Write the Label Llama formated output to this JSON file.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
