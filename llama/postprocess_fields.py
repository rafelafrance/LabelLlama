#!/usr/bin/env python3

import argparse
import logging
import textwrap
from pathlib import Path
from typing import Any

import dspy
from tqdm import tqdm

from llama.common import io_util, log
from llama.fields.all_fields import ALL_FIELDS


def postprocess_fields(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    df = io_util.read_to_df(args.in_file, limit=args.limit)
    field_list = [c for c in ALL_FIELDS if c in df.columns]

    if args.field:
        field_list = args.field

    input_rows = df.to_dict("records")

    if args.run_field_models:
        lm = dspy.LM(
            args.model_name,
            api_base=args.api_host,
            api_key=args.api_key,
            temperature=args.temperature,
            max_tokens=args.context_length,
            cache=not args.no_cache,
        )
        dspy.configure(lm=lm)

        for field_name in field_list:
            field_action = ALL_FIELDS[field_name]
            field_action.setup_postprocessing()

            # Record prompts for later use
            if args.log_file and hasattr(field_action, "predictor"):
                prompt = dspy.ChatAdapter().format_system_message(
                    field_action.predictor.signature
                )
                logging.info(prompt)

    output_rows = {
        r["source"]: {"source": r["source"], "text": r["text"]} for r in input_rows
    }

    for field_name in field_list:
        field_action = ALL_FIELDS[field_name]
        in_subfields = field_action.get_input_subfields()
        visible_subfields = field_action.get_visible_subfields()

        for row in tqdm(input_rows, desc=field_name):
            in_data = {k: row.get(k) for k in in_subfields}

            field = field_action(row["text"], **in_data)
            if args.run_field_models:
                field.run_field_model()

            field.cross_field_update(row)

            out_data = {k: getattr(field, k) for k in visible_subfields}

            # Print debug info
            if args.field or args.limit:
                print_debug_info(row, out_data)

            output_rows[row["source"]] |= out_data

    io_util.output_file(args.out_file, list(output_rows.values()))

    log.finished()


def print_debug_info(row: dict[str, Any], out_data: dict[str, Any]) -> None:
    print(row["source"])
    for field_name, value in out_data.items():
        if field_name in row:
            print(f"{'before ' + field_name:>40}: {row[field_name]}")
        print(f"{'after ' + field_name:>40}: {value}")
    print()


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Format and validate language model extracted text.""",
        ),
    )
    arg_parser.add_argument(
        "--in-file",
        type=Path,
        metavar="PATH",
        help="""Get the language model results to postprocess from this file.""",
    )
    arg_parser.add_argument(
        "--out-file",
        type=Path,
        help="""Write the postprocessing results to this file.
           Handles (.json, .jsonl, .csv, .tsv, .html)""",
    )
    arg_parser.add_argument(
        "--model-name",
        default="lm_studio/google/gemma-4-26b-a4b",
        help="""Use this language model. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--api-host",
        default="http://localhost:1234/v1",
        help="""URL for the language model. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--api-key",
        help="""API key.""",
    )
    arg_parser.add_argument(
        "--context-length",
        type=int,
        default=16384,
        help="""Model's context length. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="""Model's temperature. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--run-field-models",
        action="store_true",
        help="""Run field specific models to see if you can get more data from
            the primary field.""",
    )
    arg_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="""Don't use cached records?""",
    )
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    arg_parser.add_argument(
        "--field",
        action="append",
        help="""Just parse one field. Used for debugging.""",
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
