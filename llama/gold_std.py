#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

import duckdb
import Levenshtein
import pandas as pd

from llama.common import db_util
from llama.parse1_text.all_signatures import SIGNATURES


def list_action(args: argparse.Namespace) -> None:
    with duckdb.connect(args.db_path) as cxn:
        gold_jobs = cxn.execute(
            "select * from job where script = ? and action = ?",
            ["gold_std.py", "import"],
        ).pl()
        gold_jobs = gold_jobs.rows(named=True)
        print("=" * 80)
        print("Gold jobs\n")
        for job in gold_jobs:
            for field, value in job.items():
                print(f"{field:>12}: {value}")
            print()

        dwc_jobs = cxn.execute("select * from job where script = ?", ["run_lm.py"]).pl()
        dwc_jobs = dwc_jobs.rows(named=True)
        print("=" * 80)
        print("DwC jobs\n")
        for job in dwc_jobs:
            for field, value in job.items():
                print(f"{field:>12}: {value}")
            print()


def import_action(args: argparse.Namespace) -> None:
    with duckdb.connect(args.db_path) as cxn:
        job_id, job_started = db_util.add_job(cxn, __file__, args=args)

        if args.gold_csv:
            gold = duckdb.read_csv(args.gold_csv).fetchall().pl()
        else:
            gold = duckdb.read_json(args.gold_json).fetchall().pl()
        gold = gold.rows(named=True)

        select_ocr = "select image_path, ocr_id from ocr order by ocr_run_id, ocr_id;"
        ocr_rows = cxn.execute(select_ocr).pl()
        ocr_rows = ocr_rows.rows(named=True)
        ocr_ids = {Path(r["image_path"]).stem: r["ocr_id"] for r in ocr_rows}

        values = []
        for row in gold:
            ocr_key = Path(row[args.file_name]).stem
            ocr_id = ocr_ids[ocr_key]
            values += [
                [job_id, ocr_id, f, v] for f, v in row.items() if f not in args.skip
            ]

        cxn.executemany(
            "insert into dwc (job_id, ocr_id, field, value) values (?, ?, ?, ?)", values
        )

        db_util.update_elapsed(cxn, job_id, job_started)


def score_action(args: argparse.Namespace) -> None:
    df_data = []

    with duckdb.connect(args.db_path) as cxn:
        gold_rows = cxn.execute(
            f"""
            with piv as (
                with run as (select * from dwc where job_id = {args.gold_job_id})
                pivot run on field using first(value) group by ocr_id)
            select * from piv join ocr using (ocr_id) order by image_path
            """
        ).pl()
        gold_rows = gold_rows.rows(named=True)

        compare = {g["ocr_id"]: [g] for g in gold_rows}

        dwc_rows = cxn.execute(
            f"""
            with piv as (
                with run as (
                    select * from dwc where job_id = {args.dwc_job_id}
                       and ocr_id in (
                        select ocr_id from dwc where job_id = {args.gold_job_id})
                       )
                pivot run on field using first(value) group by ocr_id)
            select * from piv join ocr using (ocr_id)
            """
        ).pl()
        dwc_rows = dwc_rows.rows(named=True)

        for row in dwc_rows:
            if row["ocr_id"] in compare:
                compare[row["ocr_id"]].append(row)

        compare = {k: v for k, v in compare.items() if len(v) == 2}

        # Ordering the fields is annoying
        field_order = SIGNATURES[args.signature].output_fields.keys()
        fields = cxn.execute(f"""
            with
            fld1 as (select distinct field from dwc where job_id = {args.gold_job_id}),
            fld2 as (select distinct field from dwc where job_id = {args.dwc_job_id})
            select fld1.field from fld1 join fld2 using (field)
            """).fetchall()
        fields = [f[0] for f in fields]
        fields = [f for f in field_order if f in fields]

        for gold, dwc in compare.values():
            row1 = {
                "image": Path(gold["image_path"]).name,
                "ocr_text": gold["ocr_text"],
                "row": "gold",
            }
            row2 = {"image": "", "ocr_text": "", "row": "dwc"}
            row3 = {"image": "", "ocr_text": "", "row": "score"}

            for field in fields:
                row1[field] = gold.get(field, "")
                row2[field] = dwc.get(field, "")
                row3[field] = Levenshtein.ratio(row1[field], row2[field])

            df_data += [row1, row2, row3]

    df = pd.DataFrame(df_data)
    with pd.ExcelWriter(args.output, engine="odf") as writer:
        df.to_excel(writer, sheet_name="compare", index=False)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Manipulate annotated specimen metadata."""),
    )
    subparsers = arg_parser.add_subparsers(
        title="Subcommands",
        description="Actions on gold standard records",
        dest="action",
    )

    # ------------------------------------------------------------
    list_parser = subparsers.add_parser(
        "list",
        help="""List gold standard jobs and DwC jobs so you choose their IDs.""",
    )
    list_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        help="""Path to the database.""",
    )
    list_parser.set_defaults(func=list_action)

    # ------------------------------------------------------------
    import_parser = subparsers.add_parser(
        "import",
        help="""Import a gold standard from a CSV or JSON file.""",
    )
    import_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        help="""Path to the database.""",
    )
    import_parser.add_argument(
        "--gold-csv",
        type=Path,
        help="""Import data from this CSV file.""",
    )
    import_parser.add_argument(
        "--gold-json",
        type=Path,
        help="""Import data from this JSON file.""",
    )
    import_parser.add_argument(
        "--file-name",
        required=True,
        help="""The file name field used to link OCR records to the gold data.""",
    )
    import_parser.add_argument(
        "--skip",
        action="append",
        help="""Skip this column in the CSV file or field in the JSON file.
            You may use this argument more than once. Quote this argument if there are
            odd characters or spaces in the column name.""",
    )
    import_parser.add_argument(
        "--notes",
        help="""A brief description of the gold standard.""",
    )
    import_parser.set_defaults(func=import_action)

    # ------------------------------------------------------------
    score_parser = subparsers.add_parser(
        "score",
        help="""Score a Darwin Core job(s) against a gold standard.""",
    )
    score_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        help="""Path to the database.""",
    )
    score_parser.add_argument(
        "--gold-job-id",
        type=int,
        required=True,
        help="""The job ID for the gold dataset.""",
    )
    score_parser.add_argument(
        "--dwc-job-id",
        type=int,
        # action="append",
        required=True,
        help="""The job ID for the DwC dataset. You may use this more than once.""",
    )
    score_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="""Write the results to this file.""",
    )
    signatures = list(SIGNATURES.keys())
    score_parser.add_argument(
        "--signature",
        choices=signatures,
        default=signatures[0],
        help="""What type of data are you extracting? What is its signature?
            This is used to order fields in the output.""",
    )
    score_parser.set_defaults(func=score_action)

    # ------------------------------------------------------------
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    ARGS.func(ARGS)
