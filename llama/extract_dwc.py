#!/usr/bin/env python3
"""Extract Darwin Core (DwC) fields from OCRed text."""

import argparse
import sys
import textwrap
from datetime import datetime
from pathlib import Path

import dspy
import duckdb
import polars as pl
from tqdm import tqdm

from llama.modules.dwc_extract import DwcExtract
from llama.signatures.all_signatures import SIGNATURES


def extract_dwc(args: argparse.Namespace) -> None:
    """Extract Darwin Core information from the texts."""
    create_dwc_tables(args.db_path, args.signature)

    signature = SIGNATURES[args.signature]

    names = ", ".join(f"{f}" for f in signature.output_fields)
    vars_ = ", ".join(f"${f}" for f in signature.output_fields)
    insert_dwc = f"""
        insert into dwc
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
        demos=predictor.demos,
        inputs={k: f"{{{k}}}" for k in predictor.signature.input_fields},
    )

    with duckdb.connect(args.db_path) as cxn:
        ocr_recs = select_records(args.db_path, args.ocr_run_id, args.limit)
        rows = ocr_recs.rows(named=True)
        if not rows:
            sys.exit(f"No OCR records found with ID {args.ocr_run_id}")

        run_id = cxn.execute(
            """
            insert into dwc_run (
                prompt, model, api_host, notes, temperature, max_tokens, specimen_type
            )
            values (?, ?, ?, ?, ?, ?, ?)
            returning dwc_run_id;
            """,
            [
                prompt,
                args.model_name,
                args.api_host,
                args.notes.strip(),
                args.temperature,
                args.context_length,
                args.specimen_type,
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


def select_records(
    db_path: Path, ocr_run_id: int, limit: int | None = None
) -> pl.DataFrame:
    sql = "select * from ocr where ocr_run_id = ?"

    with duckdb.connect(db_path) as cxn:
        if limit:
            sql += " limit ?"
            return cxn.execute(sql, [ocr_run_id, limit]).pl()

        return cxn.execute(sql, [ocr_run_id]).pl()


def create_dwc_tables(db_path: Path, specimen_type: str) -> None:
    # Fields specific to the specimen type
    sig = SIGNATURES[specimen_type]
    fields = [f"{f} char[]," for f in sig.output_fields]
    fields = "\n".join(fields)

    sql = f"""
        create sequence if not exists dwc_run_seq;
        create table if not exists dwc_run (
            dwc_run_id integer primary key default nextval('dwc_run_seq'),
            prompt        char,
            model         char,
            api_host      char,
            notes         char,
            temperature   float,
            max_tokens    integer,
            specimen_type char,
            dwc_run_elapsed char,
            dwc_run_started timestamptz default current_localtimestamp(),
        );

        create sequence if not exists dwc_id_seq;
        create table if not exists dwc (
            dwc_id integer primary key default nextval('dwc_id_seq'),
            dwc_run_id  integer references dwc_run(dwc_run_id),
            ocr_id      integer references ocr(ocr_id),
            dwc_elapsed char,
            {fields}
        );
        """

    with duckdb.connect(db_path) as cxn:
        cxn.execute(sql)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Extract Darwin Core information from text."""),
    )

    sigs = list(SIGNATURES.keys())
    arg_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )

    arg_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )

    arg_parser.add_argument(
        "--ocr-run-id",
        type=int,
        required=True,
        action="append",
        help="""Parse records from this OCR run.""",
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
    extract_dwc(ARGS)
