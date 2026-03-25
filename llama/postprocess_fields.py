#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

import dspy
import pandas as pd
from tqdm import tqdm

from llama.common import log
from llama.postprocess.all_fields import ALL_ACTIONS


def postprocess_fields(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    df = pd.read_csv(args.lm_tsv, sep="\t")
    field_list = [c for c in ALL_ACTIONS if c in df.columns]
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
            ALL_ACTIONS[field_name].setup_field()

    output_rows = {
        r["source"]: {"source": r["source"], "text": r["text"]} for r in input_rows
    }

    for field_name in field_list:
        field_action = ALL_ACTIONS[field_name]
        in_fields = field_action.get_input_fields()
        out_fields = field_action.get_output_fields()

        for row in tqdm(input_rows, desc=field_name):
            in_data = {k: row.get(k) for k in in_fields}

            field = field_action(**in_data)
            if args.run_field_models:
                field.run_field_model()

            out_data = {k: getattr(field, k) for k in out_fields}

            output_rows[row["source"]] |= out_data

    df = pd.DataFrame(output_rows.values()).fillna("").set_index("source").sort_index()
    df.to_csv(args.output_tsv, sep="\t")

    log.finished()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Format and validate language model extracted text.""",
        ),
    )
    arg_parser.add_argument(
        "--lm-tsv",
        type=Path,
        metavar="PATH",
        help="""Write the results to this spreadsheet.""",
    )
    arg_parser.add_argument(
        "--output-tsv",
        type=Path,
        metavar="PATH",
        help="""Write the results to this spreadsheet.""",
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
        help="""Append logging notices to this file.""",
    )
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    postprocess_fields(ARGS)
