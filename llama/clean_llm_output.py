#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from llama.pylib import log, prompt_util


def postprocess_fields(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    df = pd.read_csv(args.parse_file, dtype=str).fillna("")

    prompt = prompt_util.Prompt.load(args.prompt)
    field_classes = prompt.field_classes

    columns = df.columns
    if args.column:
        columns = args.column
    columns = [c for c in columns if c not in ("source", "text", "elapsed", "status")]
    columns = [c for c in columns if c in prompt.column_names and c in field_classes]

    input_rows = [r for r in df.to_dict("records") if r["status"] == "success"]
    input_rows = input_rows[: args.limit]

    output_rows = []

    for in_row in tqdm(input_rows):
        out_row = {"source": in_row["source"], "text": in_row["text"]}

        for column in columns:
            field_action = field_classes[column]

            in_data = {k: in_row.get(k) for k in field_action.get_field_names()}

            out_field = field_action(**in_data)
            out_field.cross_field_update(in_row)

            out_data = {
                k: getattr(out_field, k) for k in out_field.get_visible_fields()
            }
            out_row |= out_data

            if debugging(args):
                print_debug_info(in_row, out_data)

        output_rows.append(out_row)

    df = pd.DataFrame(output_rows)
    df.to_csv(args.clean_file, index=False)

    log.job_elapsed(job_began)


def debugging(args: argparse.Namespace) -> bool:
    return args.column or args.limit


def print_debug_info(in_row: dict[str, Any], out_row: dict[str, Any]) -> None:
    print(in_row["source"])
    trimmed = {k: v for k, v in out_row.items() if k not in ("source", "text")}
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
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--parse-file",
        type=Path,
        required=True,
        metavar="path",
        help="""Clean the LM in this results CSV file.""",
    )
    io_group.add_argument(
        "--clean-file",
        type=Path,
        required=True,
        metavar="path",
        help="""Write the cleaned data to this CSV file.""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt",
        type=Path,
        required=True,
        metavar="path",
        help="""A markdown file with a prompt and list of fields to parse.
            It is used to get the correct version of the cleaner modules.""",
    )
    logging_group = arg_parser.add_argument_group("logging options")
    logging_group.add_argument(
        "--log-file",
        type=Path,
        metavar="path",
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    logging_group.add_argument(
        "--notes",
        metavar="string",
        help="""Notes for logging. They only appear in the log file.""",
    )
    debugging_group = arg_parser.add_argument_group("debugging options")
    debugging_group.add_argument(
        "--column",
        action="append",
        metavar="string",
        help="""Just parse one column.""",
    )
    debugging_group.add_argument(
        "--limit",
        type=int,
        metavar="int",
        help="""Limit to this many records.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    postprocess_fields(ARGS)
