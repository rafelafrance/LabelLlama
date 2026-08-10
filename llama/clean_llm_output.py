#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from llama.parser_utils.parser_cleaner import ParserCleaner
from llama.pylib import log


def postprocess_fields(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    df = pd.read_csv(args.parse_file, dtype=str).fillna("")

    cleaner = ParserCleaner.load(args.prompt)

    columns = [c for c in df.columns if c in cleaner.field_names]
    calc_columns = [c for c in df.columns if c in cleaner.calc_field_names]

    input_rows = [r for r in df.to_dict("records") if r["status"] == "success"]
    input_rows = input_rows[: args.limit]

    output_rows = []

    for in_row in tqdm(input_rows):
        out_row = {"source": in_row["source"], "text": in_row["text"]}

        for column in columns:
            field_action = cleaner.field_classes[column]

            in_data = {k: in_row.get(k) for k in field_action.get_field_names()}

            out_field = field_action(**in_data)
            out_data = {
                k: getattr(out_field, k) for k in out_field.get_visible_fields()
            }
            out_row |= out_data

        for column in calc_columns:
            field_action = cleaner.calc_field_classes[column]

            in_data = {
                k: out_row.get(k, in_row.get(k)) for k in field_action.get_field_names()
            }

            out_field = field_action(**in_data)
            out_data = {
                k: getattr(out_field, k) for k in out_field.get_visible_fields()
            }
            out_row |= out_data

        output_rows.append(out_row)

    df = pd.DataFrame(output_rows)
    df.to_csv(args.clean_file, index=False)

    log.job_elapsed(job_began)


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
