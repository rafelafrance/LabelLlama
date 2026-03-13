#!/usr/bin/env python3

import argparse
import textwrap
from collections import defaultdict
from pathlib import Path

import dspy
import duckdb
import pandas as pd
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
    lm = dspy.LM(
        args.model_name,
        api_base=args.api_host,
        api_key=args.api_key,
        temperature=args.temperature,
        max_tokens=args.context_length,
        cache=args.cache,
    )
    dspy.configure(lm=lm)

    dwc_query = """
                select ocr_id, ocr_text, image_path, dwc_id, value
                from dwc
                         join ocr using (ocr_id)
                where dwc_run_id = ?
                  and field = ?
                  and value <> '';
                """
    gold_query = """
                 select ocr_id, ocr_text, image_path, gold_id, value
                 from gold
                          join ocr using (ocr_id)
                 where gold_run_id = ?
                   and field = ?
                   and value <> '';
                 """
    dwc_fields_query = """select distinct field
                          from dwc
                          where dwc_run_id = ?;"""
    gold_fields_query = """select distinct field
                           from gold
                           where gold_run_id = ?;"""

    with duckdb.connect(args.db_path) as cxn:
        # Get list of fields
        if args.dwc_run_id:
            fields = cxn.execute(dwc_fields_query, [args.dwc_run_id]).pl()
        else:
            fields = cxn.execute(gold_fields_query, [args.gold_run_id]).pl()
        fields = {f["field"] for f in fields.rows(named=True)}

        fields = fields & {args.field} if args.field else fields
        fields = [f for f in FIELD_ACTIONS if f in fields]

        data = defaultdict(dict)

        for field in fields:
            print(field)

            actions = FIELD_ACTIONS[field](verbatim=field)

            # Get field values
            if args.dwc_run_id:
                rows = cxn.execute(dwc_query, [args.dwc_run_id, field]).pl()
            else:
                rows = cxn.execute(gold_query, [args.gold_run_id, field]).pl()
            rows = rows.rows(named=True)

            for i, row in tqdm(enumerate(rows)):
                if args.limit and i >= args.limit:
                    break
                # print(f"{row['value']=}")
                prediction = actions(text=row["value"], ocr_text=row["ocr_text"])
                data[row["image_path"]] |= prediction

                # pp(prediction)
                # print()

        for path, row in data.items():
            row["image_path"] = Path(path).name

        df = pd.DataFrame(data.values()).set_index("image_path").sort_index()
        with pd.ExcelWriter(args.results_ods, engine="odf") as writer:
            df.to_excel(writer, sheet_name="compare")


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
        "--lm-job-id",
        type=int,
        help="""Post process fields from this .""",
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
        "--cache",
        action="store_true",
        help="""Use cached records?""",
    )
    postprocess_parser.add_argument(
        "--field",
        help="""Just parse one field. Used for debugging.""",
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
