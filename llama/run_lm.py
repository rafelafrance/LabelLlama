#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path
from typing import Any

import dspy
import duckdb
from _duckdb import DuckDBPyConnection
from dspy import Prediction
from tqdm import tqdm

from llama.common import db_util
from llama.lm.all_signatures import SIGNATURES
from llama.lm.dwc_module import DwcModule


# ----------------------------------------------------------------------------------
def list_action(args: argparse.Namespace) -> None:
    with duckdb.connect(args.db_path) as cxn:
        ocr_jobs = cxn.execute("select * from jobs where action = ?", ["ocr"]).pl()
        ocr_jobs = ocr_jobs.rows(named=True)
        print("=" * 80)
        print("OCR jobs\n")
        for job in ocr_jobs:
            for field, value in job.items():
                print(f"{field:>12}: {value}")
            print()


# ----------------------------------------------------------------------------------
def extract_action(args: argparse.Namespace) -> None:
    lm = dspy.LM(
        args.model_name,
        api_base=args.api_host,
        api_key=args.api_key,
        temperature=args.temperature,
        max_tokens=args.context_length,
        cache=not args.no_cache,
    )
    dspy.configure(lm=lm)

    predictor = DwcModule(args.signature)

    prompt = get_prompt(predictor)

    with duckdb.connect(args.db_path) as cxn:
        job_id, job_started = db_util.add_job(
            cxn, __file__, args=args, params={"prompt": prompt}
        )

        docs = get_docs(cxn, args.doc_job_id)

        for doc in tqdm(docs):
            prediction = predictor(text=doc["doc_text"])

            write_predicted_fields(cxn, doc, job_id, prediction)

        db_util.update_elapsed(cxn, job_id, job_started)


def write_predicted_fields(
    cxn: DuckDBPyConnection, doc: dict[str, dict], job_id: int, prediction: Prediction
) -> None:
    values = []
    for field, value in prediction.toDict().items():
        if isinstance(value, list):
            value = " ".join(value) if len(value) > 0 else ""

        values.append([job_id, doc["doc_id"], field, value])

    cxn.executemany(
        "insert into fields (job_id, doc_id, field, value) values (?, ?, ?, ?)",
        values,
    )


def get_prompt(predictor: DwcModule) -> Any:
    adapter = dspy.ChatAdapter()
    prompt = adapter.format(
        predictor.signature,
        demos=predictor.predictor.demos,
        inputs={k: f"{{{k}}}" for k in predictor.signature.input_fields},
    )
    return prompt


def get_docs(cxn: DuckDBPyConnection, doc_job_id: int) -> list[dict[str, Any]]:
    """Get docs to parse."""
    docs = cxn.execute(
        """select doc_id, doc_text from docs where job_id = ? doc_text is not null""",
        [doc_job_id],
    ).pl()
    if not docs:
        raise RuntimeError
    docs = docs.rows(named=True)
    return docs


# ----------------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Extract Darwin Core (DwC) information from text.""",
        ),
    )
    subparsers = arg_parser.add_subparsers(
        title="Subcommands",
        description="Actions for extracting Darwin Core records",
    )

    # ------------------------------------------------------------
    list_parser = subparsers.add_parser(
        "list",
        help="""List data to help you decide which OCR runs to extract.""",
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
        "extract",
        help="""Extract DwC data from OCR records.""",
    )
    extract_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )
    signatures = list(SIGNATURES.keys())
    extract_parser.add_argument(
        "--signature",
        choices=signatures,
        default=signatures[0],
        help="""What type of data are you extracting? What is its signature?""",
    )
    extract_parser.add_argument(
        "--doc-job-id",
        type=int,
        action="append",
        help="""Parse doc records from this job.""",
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
        default=65536,
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
        "--no-cache",
        action="store_true",
        help="""Don't use cached records?""",
    )
    extract_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the number of records to parse. Used for debugging.""",
    )
    extract_parser.set_defaults(func=extract_action)

    # ------------------------------------------------------------
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    db_util.create_tables(ARGS.db_path)
    ARGS.func(ARGS)
