#!/usr/bin/env python3
"""
Extract Darwin Core (DwC) fields from OCRed text.

Note:
`export  POLARS_IMPORT_INTERVAL_AS_STRUCT=1`
before running this notebook.

"""

import argparse
import textwrap
from datetime import datetime
from pathlib import Path

import dspy
import duckdb
from tqdm import tqdm

from llama.data_formats import specimen_types


def miprov2_dwc(args: argparse.Namespace) -> None:
    spec_type = specimen_types.SPECIMEN_TYPES[args.specimen_type]

    lm = dspy.LM(
        args.model_name,
        api_base=args.api_host,
        api_key=args.api_key,
        temperature=args.temperature,
        max_tokens=args.context_length,
        cache=args.cache,
    )
    dspy.configure(lm=lm)

    predictor = dspy.Predict(spec_type)

    adapter = dspy.ChatAdapter()
    prompt = adapter.format(
        predictor.signature,
        demos=predictor.demos,
        inputs={k: f"{{{k}}}" for k in predictor.signature.input_fields},
    )

    with duckdb.connect(args.db_path) as cxn:
        pre_dwc_input = select_records(args.db_path, args.gold_run_id, args.limit)

        for pre_dwc_rec in tqdm(rows):
            rec_began = datetime.now()

            prediction = predictor(text=pre_dwc_rec["pre_dwc_text"])


def select_records(
    db_path: Path, pre_dwc_run_id: int, limit: int | None = None
) -> list:
    run_ids = ", ".join(str(i) for i in pre_dwc_run_id)
    sql = f"select * from pre_dwc where pre_dwc_run_id in ({run_ids})"
    if limit:
        sql += f" limit {limit}"

    with duckdb.connect(db_path) as cxn:
        return cxn.execute(sql).pl()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Extract Darwin Core information from text."""),
    )

    spec_types = list(specimen_types.SPECIMEN_TYPES.keys())
    arg_parser.add_argument(
        "--specimen-type",
        choices=spec_types,
        default=spec_types[0],
        help="""What type of data are you extracting.""",
    )

    arg_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )

    arg_parser.add_argument(
        "--gold-run-id",
        type=int,
        required=True,
        help="""Use this gold standard for scoring.""",
    )

    arg_parser.add_argument(
        "--model-name",
        default="lm_studio/google/gemma-3-27b",
        help="""Use this language model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--api-host",
        default="http://localhost:1234/v1",
        help="""URL for the LM model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--api-key",
        help="""API key.""",
    )

    arg_parser.add_argument(
        "--context-length",
        type=int,
        default=4096,
        help="""Model's context length. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="""Model's temperature. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        help="""Notes about this dataset.""",
    )

    arg_parser.add_argument(
        "--cache",
        action="store_true",
        help="""Use cached records?""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the number of records to parse?""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    miprov2_dwc(ARGS)
