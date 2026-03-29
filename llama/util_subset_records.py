#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

from llama.common import io_util, log


def sample_records(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    all_in = io_util.read_list_of_dicts(args.all_in)
    all_in = {r["source"]: r for r in all_in}

    sources_in = io_util.read_list_of_dicts(args.sources_in)
    sources_in = sorted({r["source"] for r in sources_in})

    sampled_out = []
    for source in sources_in:
        rec = all_in[source]
        sampled_out.append(rec)

    io_util.output_file(args.out_file, sampled_out)

    log.finished()


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
            Create a subset of records from a larger set of records & a list of sources.

            Example: You're given a gold standard list of records from an outside
            source. It would be handy to have a separate file of only the OCRed records
            in the gold standard.
            """
        ),
    )
    arg_parser.add_argument(
        "--all-in",
        type=Path,
        required=True,
        help="""The large file being to subset.
           Handles (.json, .jsonl, .csv, .tsv).""",
    )
    arg_parser.add_argument(
        "--sources-in",
        type=Path,
        required=True,
        help="""The file with sources that will be in the subset.
           Handles (.json, .jsonl, .csv, .tsv).""",
    )
    arg_parser.add_argument(
        "--out-file",
        type=Path,
        help="""Write the sampled data to this file.
           Handles (.json, .jsonl, .csv, .tsv, .html).""",
    )
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    sample_records(ARGS)
