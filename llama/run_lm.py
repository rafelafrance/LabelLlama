#!/usr/bin/env python3

import argparse
import random
import textwrap
from datetime import datetime
from pathlib import Path

import dspy
import duckdb
from tqdm import tqdm

from llama.modules.dwc_extract import DwcExtract
from llama.pylib.db_util import create_dwc_tables, display_runs
from llama.signatures.all_signatures import SIGNATURES


def list_action(args: argparse.Namespace) -> None:
    create_dwc_tables(args.db_path, args.signature)

    display_runs(args.db_path, "ocr_run")
    display_runs(args.db_path, "dwc_run")


def extract_action(args: argparse.Namespace) -> None:
    create_dwc_tables(args.db_path)

    job_began = datetime.now()

    lm = dspy.LM(
        args.model_name,
        api_base=args.api_host,
        api_key=args.api_key,
        temperature=args.temperature,
        max_tokens=args.context_length,
        cache=args.cache,
    )
    dspy.configure(lm=lm)

    predictor = DwcExtract(args.signature)

    adapter = dspy.ChatAdapter()
    prompt = adapter.format(
        predictor.signature,
        demos=predictor.predictor.demos,
        inputs={k: f"{{{k}}}" for k in predictor.signature.input_fields},
    )

    with duckdb.connect(args.db_path) as cxn:
        ocr_recs = []

        notes = args.notes or ""

        # Get OCR records
        if args.ocr_run_id:
            ocr_ids = ", ".join(str(i) for i in args.ocr_run_id)
            query = f"""
                select distinct ocr_id, ocr_text
                  from ocr where ocr_run_id in ({ocr_ids})
                """
            rows = cxn.execute(query).pl()
            rows = rows.rows(named=True)
            ocr_recs += rows
            notes += f" OCR run IDs {ocr_ids} "

        # Get OCR records via gold data
        if args.gold_run_id:
            gold_ids = ", ".join(str(i) for i in args.gold_run_id)
            query = f"""
                select distinct ocr_id, ocr_text
                  from gold join ocr using (ocr_id)
                 where gold_run_id in ({gold_ids});"""
            rows = cxn.execute(query).pl()
            rows = rows.rows(named=True)
            ocr_recs += rows
            notes += f" gold run IDs {gold_ids} "

        # Limit and shuffle OCR records
        if args.limit:
            if args.seed is not None:
                random.seed(args.seed)
            random.shuffle(rows)
            rows = rows[: args.limit]
            notes += f" limit {args.limit} "

        notes = notes.strip()

        # Start adding DwC data
        dwc_run_id = cxn.execute(
            """
            insert into dwc_run (
                prompt, model, api_host, notes, temperature, max_tokens, signature
            ) values (?, ?, ?, ?, ?, ?, ?) returning dwc_run_id;
            """,
            [
                prompt,
                args.model_name,
                args.api_host,
                notes,
                args.temperature,
                args.context_length,
                args.signature,
            ],
        ).fetchone()[0]

        for ocr_rec in tqdm(rows):
            prediction = predictor(text=ocr_rec["ocr_text"])

            for field, value in prediction.toDict().items():
                value = " ".join(value) if value else ""
                cxn.execute(
                    query="""
                        insert into dwc (dwc_run_id, ocr_id, field, value)
                        values ($dwc_run_id, $ocr_id, $field, $value);
                        """,
                    parameters={
                        "dwc_run_id": dwc_run_id,
                        "ocr_id": ocr_rec["ocr_id"],
                        "field": field,
                        "value": value,
                    },
                )

        cxn.execute(
            "update dwc_run set dwc_run_elapsed = ? where dwc_run_id = ?;",
            [str(datetime.now() - job_began), dwc_run_id],
        )


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Extract Darwin Core (DwC) information from text."""
        ),
    )
    subparsers = arg_parser.add_subparsers(
        title="Subcommands", description="Actions for extracting Darwin Core records"
    )

    # ------------------------------------------------------------
    list_parser = subparsers.add_parser(
        "list",
        help="""List data to help you decide which OCR runs to extract.""",
    )
    sigs = list(SIGNATURES.keys())
    list_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )
    list_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )
    list_parser.set_defaults(func=list_action)

    # ------------------------------------------------------------
    extract_parser = subparsers.add_parser(
        "extract", help="""Extract DwC data from OCR records."""
    )
    extract_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )
    sigs = list(SIGNATURES.keys())
    extract_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )
    extract_parser.add_argument(
        "--ocr-run-id",
        type=int,
        action="append",
        help="""Parse records from this OCR run. You may do this more than once.""",
    )
    extract_parser.add_argument(
        "--gold-run-id",
        type=int,
        action="append",
        help="""Parse records from this gold run. You may do this more than once.""",
    )
    extract_parser.add_argument(
        "--model-name",
        default="lm_studio/google/gemma-3-27b",
        help="""Use this language model. (default: %(default)s)""",
    )
    extract_parser.add_argument(
        "--api-host",
        # default="http://localhost:1234/v1",
        help="""URL for the LM model.""",
    )
    extract_parser.add_argument(
        "--api-key",
        help="""API key.""",
    )
    extract_parser.add_argument(
        "--context-length",
        type=int,
        default=4096,
        help="""Model's context length. (default: %(default)s)""",
    )
    extract_parser.add_argument(
        "--temperature",
        type=float,
        help="""Model's temperature. (default: %(default)s)""",
    )
    extract_parser.add_argument(
        "--notes",
        default="",
        help="""Notes about this dataset.""",
    )
    extract_parser.add_argument(
        "--cache",
        action="store_true",
        help="""Use cached records?""",
    )
    extract_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the number of records to parse.""",
    )
    extract_parser.add_argument(
        "--seed",
        type=int,
        help="""Use this seed to select a random sample of limit records.""",
    )
    extract_parser.set_defaults(func=extract_action)

    # ------------------------------------------------------------

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    ARGS.func(ARGS)
