#!/usr/bin/env python3
"""Extract Darwin Core (DwC) fields from OCRed text."""

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
    signature = SIGNATURES[args.signature]

    names = ", ".join(f"{f}" for f in signature.output_fields)
    vars_ = ", ".join(f"${f}" for f in signature.output_fields)
    insert_dwc = f"""
        insert into dwc_{args.signature}
            (dwc_run_id, ocr_id, dwc_elapsed, {names})
            values ($dwc_run_id, $ocr_id, $dwc_elapsed, {vars_});
        """

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
        rows = select_ocr_recs(args.db_path, args.ocr_run_id, args.limit, args.seed)

        run_id = cxn.execute(
            """
            insert into dwc_run (
                prompt, model, api_host, notes, temperature, max_tokens, specimen_type
            ) values (?, ?, ?, ?, ?, ?, ?) returning dwc_run_id;
            """,
            [
                prompt,
                args.model_name,
                args.api_host,
                args.notes.strip(),
                args.temperature,
                args.context_length,
                args.signature,
            ],
        ).fetchone()[0]

        for ocr_rec in tqdm(rows):
            rec_began = datetime.now()

            prediction = predictor(text=ocr_rec["ocr_text"])

            cxn.execute(
                insert_dwc,
                {
                    "dwc_run_id": run_id,
                    "ocr_id": ocr_rec["ocr_id"],
                    "dwc_elapsed": datetime.now() - rec_began,
                }
                | prediction.toDict(),
            )

        cxn.execute(
            "update dwc_run set dwc_run_elapsed = ? where dwc_run_id = ?;",
            [datetime.now() - job_began, run_id],
        )


def select_ocr_recs(
    db_path: Path, ocr_run_id: list[int], limit: int = 0, seed: int | None = None
) -> list[dict]:
    run_ids = ", ".join(str(i) for i in ocr_run_id)
    query = f"select ocr_id, ocr_text from ocr where ocr_run_id in ({run_ids})"

    with duckdb.connect(db_path) as cxn:
        ocr_recs = cxn.execute(query).pl()

    rows = ocr_recs.rows(named=True)

    if seed is not None:
        random.seed(seed)
        random.shuffle(rows)

    if limit:
        rows = rows[:limit]

    return rows


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
        required=True,
        action="append",
        help="""Parse records from this OCR run. You may do this more than once.""",
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
