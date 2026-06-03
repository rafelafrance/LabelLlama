#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path
from typing import Any

from tqdm import tqdm

from llama.pylib import io_util, log, prompt_util

DEBUG_SKIP = ("source", "text")


def postprocess_fields(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    df = io_util.read_to_df(args.in_file, limit=args.limit)

    field_list = prompt_util.read_field_list(args.prompt)
    field_classes = prompt_util.field_classes_by_column_name(field_list)
    headers = list(field_classes.keys())

    columns = df.columns
    if args.column:
        columns = args.column
    columns = [c for c in columns if c not in ("source", "text", "elapsed")]
    columns = [c for c in columns if c in headers]

    input_rows = df.to_dict("records")
    input_rows = input_rows[: args.limit]

    output_rows = []

    for in_row in tqdm(input_rows):
        out_row = {"source": in_row["source"], "text": in_row["text"]}

        for column in columns:
            field_action = field_classes[column]

            in_data = {k: in_row.get(k) for k in field_action.get_input_fields()}

            out_field = field_action(in_row["text"], **in_data)
            out_field.cross_field_update(in_row)

            out_data = {
                k: getattr(out_field, k) for k in out_field.get_visible_fields()
            }
            out_row |= out_data

            if debugging(args):
                print_debug_info(in_row, out_data)

        output_rows.append(out_row)

    io_util.output_file(args.out_file, output_rows)

    log.finished()


def debugging(args: argparse.Namespace) -> bool:
    return args.column or args.limit


def print_debug_info(in_row: dict[str, Any], out_row: dict[str, Any]) -> None:
    print(in_row["source"])
    trimmed = {k: v for k, v in out_row.items() if k not in DEBUG_SKIP}
    for column, value in trimmed.items():
        if column in in_row:
            print(f"{'before ' + column:>40}: {in_row[column]}")
        print(f"{'after ' + column:>40}: {value}")
    print()


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Format and validate language model (LM) extracted text.""",
        ),
    )
    arg_parser.add_argument(
        "--prompt",
        type=Path,
        required=True,
        help="""A markdown file with a prompt and list of fields to parse.
            It is used to get the correct version of the cleaner modules.""",
    )
    arg_parser.add_argument(
        "--in-file",
        type=Path,
        metavar="PATH",
        help="""Clean the LM this results in this file.""",
    )
    arg_parser.add_argument(
        "--out-file",
        type=Path,
        help="""Write the postprocessing results to this file.
           Handles (.json, .jsonl, .csv, .tsv, .html)""",
    )
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    arg_parser.add_argument(
        "--notes",
        help="""Notes for logging.""",
    )
    arg_parser.add_argument(
        "--column",
        action="append",
        help="""Just parse one column. Used for debugging.""",
    )
    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit to this many records. Used for debugging.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    postprocess_fields(ARGS)
