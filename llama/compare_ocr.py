#!/usr/bin/env python3

import argparse
import textwrap
from collections import defaultdict
from pathlib import Path

import pandas as pd

from llama.pylib import log


def compare(args: argparse.Namespace) -> None:
    """Compare LLM outputs against gbif data and write an HTML report."""
    job_began = log.job_began(args.log_file, args=args)

    all_ocr = defaultdict(list)
    for ocr_file in args.ocr_file:
        ocr = pd.read_csv(ocr_file, dtype=str).fillna("").to_dict("records")
        for row in ocr:
            all_ocr[row["source"]].append(row)

    for i, (key, value) in enumerate(all_ocr.items(), 1):
        print("=" * 90)
        print(i, key)
        print()
        print("-" * 80)
        for row in value:
            print(row["elapsed"])
            print()
            print(row["text"])
            print("-" * 80)
        print()
        if i == 10:
            break

    log.job_elapsed(job_began)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Compare OCR results from different models."""),
    )
    arg_parser.add_argument(
        "--ocr-file",
        type=Path,
        required=True,
        action="append",
        metavar="path",
        help="""This file contains the original OCRed text.""",
    )
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        metavar="string",
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    arg_parser.add_argument(
        "--notes",
        metavar="string",
        help="""Notes for logging. They only appear in the log file.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    compare(ARGS)
