#!/usr/bin/env python3

import argparse
import textwrap
from argparse import Namespace
from collections import defaultdict
from pathlib import Path
from typing import Any

import dspy
import duckdb
import pandas as pd
from _duckdb import DuckDBPyConnection
from tqdm import tqdm

from llama.common import db_util
from llama.postprocess.all_actions import FIELD_ACTIONS


# ----------------------------------------------------------------------------------
def list_action(args: argparse.Namespace) -> None:
    with duckdb.connect(args.db_path) as cxn:
        ocr_jobs = cxn.execute("select * from job where action = ?", ["extract"]).pl()
        ocr_jobs = ocr_jobs.rows(named=True)
        print("=" * 80)
        print("LM extraction jobs\n")
        for job in ocr_jobs:
            for field, value in job.items():
                print(f"{field:>12}: {value}")
            print()


# ----------------------------------------------------------------------------------
def postprocess_action(args: argparse.Namespace) -> None:
    configure_lm(args)

    with duckdb.connect(args.db_path) as cxn:
        job_id, job_started = None, None
        # if not args.dry_run:
        #     job_id, job_started = db_util.add_job(cxn, __file__, args=args)

        field_list = get_field_list(cxn, args.fields_job_id, args.job_id)

        data = defaultdict(dict)

        for field in field_list:
            print(field)

            actions = FIELD_ACTIONS[field](verbatim=field)
            rows = get_field_values(cxn, field, args.job_id)

            for i, row in tqdm(enumerate(rows)):
                if args.limit and i >= args.limit:
                    break
                # print(f"{row['value']=}")
                prediction = actions(text=row["value"], doc_text=row["doc_text"])
                data[row["src_path"], row["src_id"]] |= prediction

                # pp(prediction)
                # print()

        if args.dry_run:
            return

        db_util.update_elapsed(cxn, job_id, job_started)

        for path, row in data.items():
            row["src_path"] = Path(path).name

        df = pd.DataFrame(data.values()).set_index(["src_path", "src_id"]).sort_index()
        with pd.ExcelWriter(args.results_ods, engine="odf") as writer:
            df.to_excel(writer, sheet_name="compare")


def configure_lm(args: Namespace) -> None:
    lm = dspy.LM(
        args.model_name,
        api_base=args.api_host,
        api_key=args.api_key,
        temperature=args.temperature,
        max_tokens=args.context_length,
        cache=not args.no_cache,
    )
    dspy.configure(lm=lm)


def get_field_values(
    cxn: DuckDBPyConnection, field: str, job_id: int
) -> list[dict[str, Any]]:
    value_query = """
        select doc_id, doc_text, src_path, src_id, field_id, value
        from field join doc using (doc_id)
        where job_id = ? and field = ? and value <> ''
        """
    rows = cxn.execute(value_query, [job_id, field]).pl()
    rows = rows.rows(named=True)
    return rows


def get_field_list(
    cxn: DuckDBPyConnection, fields_job_id: int, field: list[str]
) -> list[str]:
    """Get a list of fields from a LM field extraction or previous postprocess job."""
    fields_query = "select distinct field from fields where job_id = ?"
    field_list = cxn.execute(fields_query, [fields_job_id]).pl()
    field_list = {f["field"] for f in field_list.rows(named=True)}

    # Filter fields based on user input and available field actions
    field_list = field_list & {field} if field else field_list
    fields = [f for f in FIELD_ACTIONS if f in field_list]
    return fields


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
    postprocess_parser = subparsers.add_parser(
        "postprocess",
        help="""Post process fields.""",
    )
    postprocess_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )
    postprocess_parser.add_argument(
        "--results-ods",
        type=Path,
        metavar="PATH",
        help="""Write the results to this spreadsheet.""",
    )
    postprocess_parser.add_argument(
        "--job-id",
        type=int,
        help="""Post process fields from this LM or previous postprocessing job.""",
    )
    postprocess_parser.add_argument(
        "--model-name",
        default="lm_studio/google/gemma-3-27b",
        help="""Use this language model. (default: %(default)s)""",
    )
    postprocess_parser.add_argument(
        "--api-host",
        default="http://localhost:1234/v1",
        help="""URL for the LM model.""",
    )
    postprocess_parser.add_argument(
        "--api-key",
        help="""API key.""",
    )
    postprocess_parser.add_argument(
        "--context-length",
        type=int,
        default=16384,
        help="""Model's context length. (default: %(default)s)""",
    )
    postprocess_parser.add_argument(
        "--temperature",
        type=float,
        help="""Model's temperature. (default: %(default)s)""",
    )
    postprocess_parser.add_argument(
        "--notes",
        default="",
        help="""Notes about this dataset.""",
    )
    postprocess_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="""Don't use cached records?""",
    )
    postprocess_parser.add_argument(
        "--field",
        help="""Just parse one field. Used for debugging.""",
    )
    postprocess_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="""Don't write the results to the database. Used for debugging.""",
    )
    postprocess_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the number of records to parse per field. For debugging.""",
    )
    postprocess_parser.set_defaults(func=postprocess_action)

    # ------------------------------------------------------------

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    db_util.create_tables(ARGS.db_path)
    ARGS.func(ARGS)
