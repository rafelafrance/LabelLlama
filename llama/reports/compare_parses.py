#!/usr/bin/env python3

import argparse
import textwrap
from collections import defaultdict
from pathlib import Path

import pandas as pd
from rich import print as rprint

from llama.pylib import log
from llama.results.model_status import ModelStatus


def compare(args: argparse.Namespace) -> None:
    """Compare parsed LLM outputs against each other and print the differences."""
    job_began = log.job_began(None, args=args)

    all_parses = defaultdict(list)
    columns = []
    for parse_file in args.parse_file:
        parse_df = pd.read_csv(parse_file, dtype=str).fillna("")
        _check_columns(parse_file, parse_df, {"status", "source"})
        parse = [
            p for p in parse_df.to_dict("records") if p["status"] == ModelStatus.SUCCESS
        ]
        if not parse:
            continue
        for k in parse[0]:
            if k not in ("status", "source") and k not in columns:
                columns.append(k)
        for row in parse:
            all_parses[row["source"]].append(row)

    all_parses = {k: v for k, v in all_parses.items() if len(v) > 1}
    shown = list(all_parses.items())[: args.limit]

    for i, (key, value) in enumerate(shown, 1):
        print("=" * 90)
        print(i, key)
        print("-" * 80)
        for col in columns:
            values = [row.get(col, "") for row in value]
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
    print(f"{len(shown)} compared")

    log.job_elapsed(job_began)


def _check_columns(parse_file: Path, df: pd.DataFrame, required: set[str]) -> None:
    missing = required - set(df.columns)
    if missing:
        missing_str = ", ".join(sorted(missing))
        raise ValueError(f"{parse_file} is missing required columns: {missing_str}")


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
        "--limit",
        type=int,
        metavar="int",
        help="""Limit to this many records.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    compare(ARGS)
