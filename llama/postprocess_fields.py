#!/usr/bin/env python3

import argparse
import textwrap
from argparse import Namespace
from pathlib import Path
from typing import Any

import dspy
import duckdb
from duckdb import DuckDBPyConnection
from tqdm import tqdm

from llama.common import db_util
from llama.postprocess.all_fields import ALL_ACTIONS


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
        # job_id, job_started = None, None
        # if not args.dry_run:
        #     job_id, job_started = db_util.add_job(cxn, __file__, args=args)

        field_list = get_field_list(cxn, args.job_id, args.field)

        input_rows = get_input_rows(cxn, args.job_id, args.limit)

        for field in field_list:
            action = ALL_ACTIONS[field]
            in_fields = action.get_input_fields()
            out_fields = action.get_output_fields()

            for row in tqdm(input_rows):
                in_data = {k: row[k] for k in in_fields}
                print(f" {in_data=}")
                result = action(**in_data)
                out_data = {k: getattr(result, k) for k in out_fields}
                print(f"{out_data=}\n")

        # print()
        # print(f"{'raw':>24} {field_row['value']}")
        # for key, value in subfields.items():
        #     print(f"{key:>24} {value}")
        # print()

        # if args.dry_run:
        #     return
        #
        # db_util.update_elapsed(cxn, job_id, job_started)
        #
        # for path, row in data.items():
        #     row["src_path"] = Path(path).name
        #
        # df =pd.DataFrame(data.values()).set_index(["src_path", "src_id"]).sort_index()
        # with pd.ExcelWriter(args.results_ods, engine="odf") as writer:
        #     df.to_excel(writer, sheet_name="compare")


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


def get_input_rows(
    cxn: DuckDBPyConnection, job_id: int, limit: int
) -> list[dict[str, Any]]:
    value_query = f"""
        with piv as (
            with run as (select * from fields where job_id = {job_id})
            pivot run on field using first(value) group by doc_id)
        select * from piv join docs using (doc_id)
        """
    if limit:
        value_query += f" limit {limit}"
    rows = cxn.execute(value_query).df().to_dict("records")
    # rows = pl.DataFrame(rows, orient="row", infer_schema_length=None)
    # rows = rows.rows(named=True)
    return rows


def get_field_list(cxn: DuckDBPyConnection, job_id: int, field: list[str]) -> list[str]:
    """Get a list of fields from a LM field extraction or previous postprocess job."""
    fields_query = "select distinct field from fields where job_id = ?"
    field_recs = cxn.execute(fields_query, [job_id]).pl()

    # Handle debugging a single field
    field_set = {f["field"] for f in field_recs.rows(named=True)}
    field_set = field_set & {field} if field else field_set

    # The fields should be in ALL_ACTIONS order
    field_list = [f for f in ALL_ACTIONS if f in field_set]

    return field_list


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
        help="""Post process fields from this LM job or previous postprocessing job.""",
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
        default=0.1,
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
        "-q",
        "--quiet",
        action="store_true",
        help="""Do not print progress and model results to the console.""",
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
