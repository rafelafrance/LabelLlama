#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

import dspy
from tqdm import tqdm

from llama.common import io_util, log
from llama.postprocess.all_fields import ALL_FIELDS


def postprocess_fields(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    df = io_util.read_to_df(args.in_file)
    field_list = [c for c in ALL_FIELDS if c in df.columns]
    if args.field:
        field_list = [args.field]
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
            ALL_FIELDS[field_name].setup_field()

    output_rows = {
        r["source"]: {"source": r["source"], "text": r["text"]} for r in input_rows
    }

    for field_name in field_list:
        field_action = ALL_FIELDS[field_name]
        in_subfields = field_action.get_input_subfields()
        out_subfields = field_action.get_output_subfields()

        for row in tqdm(input_rows, desc=field_name):
            in_data = {k: row.get(k) for k in in_subfields}

            field = field_action(**in_data)
            if args.run_field_models:
                field.run_field_model()

            field.cross_field_update(row)

            out_data = {k: getattr(field, k) for k in out_subfields}

            output_rows[row["source"]] |= out_data

    io_util.output_file(args.out_file, list(output_rows.values()))

    log.finished()


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
        default="lm_studio/google/gemma-3-27b",
        help="""Use this language model. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--api-host",
        default="http://localhost:1234/v1",
        help="""URL for the LM model.""",
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
        "--field",
        help="""Just parse one field. Used for debugging.""",
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
    postprocess_fields(ARGS)
