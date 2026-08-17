#!/usr/bin/env python3

import argparse
import textwrap
from collections import defaultdict
from pathlib import Path

import pandas as pd
from rich import print as rprint

from llama.model_utils.model_status import ModelStatus
from llama.pylib import log


def compare(args: argparse.Namespace) -> None:
    """Compare LLM outputs against gbif data and write an HTML report."""
    job_began = log.job_began(args.log_file, args=args)

    all_parses = defaultdict(list)
    columns = []
    for parse_file in args.parse_file:
        parse = pd.read_csv(parse_file, dtype=str).fillna("").to_dict("records")
        parse = [p for p in parse if p["status"] == ModelStatus.SUCCESS]
        columns = [k for k in parse[0] if k not in ("status", "elapsed", "source")]
        for row in parse:
            all_parses[row["source"]].append(row)

    all_parses = {k: v for k, v in all_parses.items() if len(v) > 1}

    for i, (key, value) in enumerate(all_parses.items(), 1):
        print("=" * 90)
        print(i, key)
        print("-" * 80)
        for col in columns:
            values = [row[col] for row in value]
            if col == "text":
                rprint(f"[blue]{col}: {values[0]}")
            elif all(v == values[0] for v in values):
                rprint(f"[green]{col}: {values[0]}")
            else:
                for v in values:
                    rprint(f"[red]{col}: {v}")
            print("-" * 80)
        print()

    print("=" * 90)
    print(f"{len(all_parses)} compared")

    log.job_elapsed(job_began)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Compare OCR results from different models."""),
    )
    arg_parser.add_argument(
        "--parse-file",
        type=Path,
        required=True,
        action="append",
        metavar="path",
        help="""This file contains parsed text.""",
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
