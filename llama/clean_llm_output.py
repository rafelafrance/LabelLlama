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

    field_files_by_name = prompt_util.get_field_files_by_name()

    df = io_util.read_to_df(args.in_file, limit=args.limit)
    field_list = [c for c in df.columns if c in field_files_by_name]

    field_classes = prompt_util.get_field_classes(field_list)

    if args.column:
        field_list = args.column

    input_rows = df.to_dict("records")
    input_rows = input_rows[: args.limit]

    output_rows = []

    for in_row in tqdm(input_rows):
        out_row = {"source": in_row["source"], "text": in_row["text"]}

        for field_name in field_list:
            field_action = field_classes[field_name]

            in_data = {k: in_row.get(k) for k in field_action.get_input_fields()}

            out_field = field_action(in_row["text"], **in_data)

            out_field.cross_field_update(in_row)

            out_data = {
                k: getattr(out_field, k) for k in out_field.get_visible_fields()
            }
            out_row |= out_data

            if is_debugging(args):
                print_debug_info(in_row, out_data)

        output_rows.append(out_row)

    io_util.output_file(args.out_file, output_rows)

    log.finished()


def is_debugging(args: argparse.Namespace) -> bool:
    return args.column or args.limit


def print_debug_info(in_row: dict[str, Any], out_row: dict[str, Any]) -> None:
    print(in_row["source"])
    trimmed = {k: v for k, v in out_row.items() if k not in DEBUG_SKIP}
    for field_name, value in trimmed.items():
        if field_name in in_row:
            print(f"{'before ' + field_name:>40}: {in_row[field_name]}")
        print(f"{'after ' + field_name:>40}: {value}")
    print()


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Format and validate language model (LM) extracted text.""",
        ),
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
