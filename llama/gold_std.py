#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path
from typing import Any

import duckdb
import Levenshtein
import pandas as pd
from duckdb import DuckDBPyConnection

from llama.common import db_util
from llama.lm.all_signatures import SIGNATURES


# ------------------------------------------------------------------------------
def list_action(args: argparse.Namespace) -> None:
    """List jobs so you can choose a pair for scoring."""
    with duckdb.connect(args.db_path) as cxn:
        list_gold_std_jobs(cxn)
        list_lm_jobs(cxn)


def list_lm_jobs(cxn: DuckDBPyConnection) -> None:
    dwc_jobs = cxn.execute("select * from jobs where script = ?", ["run_lm.py"]).pl()
    dwc_jobs = dwc_jobs.rows(named=True)
    print("=" * 80)
    print("fields jobs\n")
    for job in dwc_jobs:
        for field, value in job.items():
            print(f"{field:>12}: {value}")
        print()


def list_gold_std_jobs(cxn: DuckDBPyConnection) -> None:
    gold_jobs = cxn.execute(
        "select * from jobs where script = ? and action = ?",
        ["gold_std.py", "import"],
    ).pl()
    gold_jobs = gold_jobs.rows(named=True)
    print("=" * 80)
    print("Gold jobs\n")
    for job in gold_jobs:
        for field, value in job.items():
            print(f"{field:>12}: {value}")
        print()


# ------------------------------------------------------------------------------
def import_action(args: argparse.Namespace) -> None:
    with duckdb.connect(args.db_path) as cxn:
        job_id, job_started = db_util.add_job(cxn, __file__, args=args)

        if args.gold_csv:
            new_gold_data = duckdb.read_csv(args.gold_csv).pl()
        else:
            new_gold_data = duckdb.read_json(args.gold_json).pl()
        new_gold_data = new_gold_data.rows(named=True)

        path_to_doc_id_map = get_path_to_doc_id_map(cxn)

        write_new_fields(
            cxn, new_gold_data, args.file_name, path_to_doc_id_map, job_id, args.skip
        )

        db_util.update_elapsed(cxn, job_id, job_started)


def write_new_fields(
    cxn: DuckDBPyConnection,
    new_gold_data: list[dict],
    file_name_field: str,
    path_to_doc_id_map: dict[str, int],
    job_id: int,
    skip: list[str],
) -> None:
    """Write new data fields to the database."""
    values = []
    for row in new_gold_data:
        path = Path(row[file_name_field]).stem
        doc_id = path_to_doc_id_map[path]
        values += [[job_id, doc_id, f, v] for f, v in row.items() if f not in skip]

    cxn.executemany(
        "insert into fields (job_id, doc_id, field, value) values (?, ?, ?, ?)",
        values,
    )


def get_path_to_doc_id_map(cxn: DuckDBPyConnection) -> dict[str, int]:
    """Input rows are indexed by file name we need to convert those into doc_ids."""
    select_ocr = "select src_path, doc_id from docs order by job_id, doc_id"
    doc_rows = cxn.execute(select_ocr).pl()
    doc_rows = doc_rows.rows(named=True)
    path_to_doc_id_map = {Path(r["src_path"]).stem: r["doc_id"] for r in doc_rows}
    return path_to_doc_id_map


# ------------------------------------------------------------------------------
def score_action(args: argparse.Namespace) -> None:
    with duckdb.connect(args.db_path) as cxn:
        gold_rows = get_gold_std_rows(cxn, args.gold_job_id)
        field_rows = get_lm_field_rows(cxn, args.gold_job_id, args.lm_job_id)

        compare = pair_gold_lm_rows(gold_rows, field_rows)

        field_order = get_field_order(
            cxn, args.signature, args.gold_job_id, args.lm_job_id
        )

        df_data = score_fields(compare, field_order)

        # Write the comparison to a spreadsheet
        df = pd.DataFrame(df_data)
        with pd.ExcelWriter(args.output, engine="odf") as writer:
            df.to_excel(writer, sheet_name="compare", index=False)


def score_fields(
    compare: dict[Any, list[dict[str, str]]], field_order: list[str]
) -> list[dict]:
    """Score the fields and add a new row with the field scores."""
    df_data: list[dict[str, str]] = []

    for gold, lm in compare.values():
        row1: dict[str, str] = {
            "source": Path(gold["src_path"]).name,
            "doc_text": gold["doc_text"],
            "row": "gold",
        }
        row2: dict[str, str] = {"source": "", "doc_text": "", "row": "lm"}
        row3: dict[str, float | str] = {
            "source": "",
            "doc_text": "",
            "row": "score",
        }

        for field in field_order:
            row1[field] = gold.get(field, "")
            row2[field] = lm.get(field, "")
            row3[field] = Levenshtein.ratio(row1[field], row2[field])

        df_data += [row1, row2, row3]
    return df_data


def get_field_order(
    cxn: DuckDBPyConnection, signature: str, gold_job_id: int, lm_job_id: int
) -> list[str]:
    """Get the report output field order across the page to help report usefulness."""
    output_fields = SIGNATURES[signature].output_fields.keys()
    field_order = cxn.execute(
        f"""
            with
            fld1 as (
                select distinct field from fields where job_id = {gold_job_id}),
            fld2 as (
                select distinct field from fields where job_id = {lm_job_id})
            select fld1.field from fld1 join fld2 using (field)
            """
    ).fetchall()
    field_order = [f[0] for f in field_order]
    field_order = [f for f in output_fields if f in field_order]
    return field_order


def pair_gold_lm_rows(
    gold_rows: list[dict], field_rows: list[dict]
) -> dict[int, list[dict]]:
    """Pair gold and LM field output for comparison."""
    # Setup rows for comparison - start with the gold data
    compare = {g["doc_id"]: [g] for g in gold_rows}

    # Add align the gold standard rows with the LM rows
    for row in field_rows:
        if row["doc_id"] in compare:
            compare[row["doc_id"]].append(row)

    # Only keep the row pairs if there is actually a pair
    compare = {k: v for k, v in compare.items() if len(v) == 2}
    return compare


def get_lm_field_rows(
    cxn: DuckDBPyConnection, gold_job_id: int, lm_job_id: int
) -> list[dict]:
    """Get the LM fields to compare against the gold standard as a fat table."""
    field_rows = cxn.execute(
        f"""
            with piv as (
                with run as (
                    select * from fields where job_id = {lm_job_id}
                       and doc_id in (
                        select doc_id from fields where job_id = {gold_job_id})
                       )
                pivot run on field using first(value) group by doc_id)
            select * from piv join docs using (doc_id)
            """
    ).pl()
    field_rows = field_rows.rows(named=True)
    return field_rows


def get_gold_std_rows(cxn: DuckDBPyConnection, gold_job_id: int) -> list[dict]:
    """Get gold standard data as a fat table."""
    gold_rows = cxn.execute(
        f"""
            with piv as (
                with run as (select * from fields where job_id = {gold_job_id})
                pivot run on field using first(value) group by doc_id)
            select * from piv join docs using (doc_id) order by src_path
            """
    ).pl()
    gold_rows = gold_rows.rows(named=True)
    return gold_rows


# ------------------------------------------------------------------------------
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
        help="""List gold standard jobs and fields jobs so you choose their IDs
            for scoring against each other.""",
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
        "--lm-job-id",
        type=int,
        required=True,
        help="""The job ID for the LM fields dataset.""",
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
