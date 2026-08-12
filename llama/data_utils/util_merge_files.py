#!/usr/bin/env python3

import argparse
import csv
import sys
import textwrap
from pathlib import Path

import pandas as pd

from llama.pylib import log

csv.field_size_limit(sys.maxsize)


def merge_files(args: argparse.Namespace) -> None:
    log.started(args=args)

    dfs = [
        pd.read_csv(path, dtype=str).fillna("") for path in Path().glob(args.input_glob)
    ]
    df = pd.concat(dfs)
    df.to_csv(args.output_file, index=False)

    log.finished()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""
            Combine multiple files (*.csv, *.tsv, etc) into a single file.
            """),
    )

    arg_parser.add_argument(
        "--input-glob",
        type=Path,
        required=True,
        metavar="PATH",
        help="""The input file glob. For example: data/files/*.csv""",
    )
    arg_parser.add_argument(
        "--output-file",
        type=Path,
        required=True,
        metavar="PATH",
        help="""The merged output file name.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    merge_files(ARGS)
