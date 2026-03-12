#!/usr/bin/env python3

import argparse
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

import duckdb

from llama.common import db_util

# import Levenshtein
# import pandas as pd


@dataclass
class Pair:
    ocr_id: int
    ocr_text: str
    dwc1: dict = field(default_factory=dict)
    dwc2: dict = field(default_factory=dict)


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

        for row in gold:
            ocr_key = Path(row[args.file_name]).stem
            ocr_id = ocr_ids[ocr_key]
            for field, value in row.items():
                if field in args.skip:
                    continue
                cxn.execute(
                    query="""
                        insert into dwc (job_id, ocr_id, field, value)
                        values ($job_id, $ocr_id, $field, $value);
                        """,
                    parameters={
                        "job_id": job_id,
                        "ocr_id": ocr_id,
                        "field": field,
                        "value": value,
                    },
                )

        db_util.update_elapsed(cxn, job_id, job_started)


def score_action(args: argparse.Namespace) -> None:
    result = duckdb.read_csv(args.in_tsv)
    print(result)
    # select_fields = """select distinct field from dwc where job_id = ?;"""
    # select_ocr_ids = """select distinct ocr_id from dwc where job_id = ?;"""
    #
    # select_dwc = """
    #     with job as (select * from dwc join ocr using(ocr_id) where job_id = ?)
    #     pivot job on field using first(value) group by ocr_id;
    #     """
    #
    # fields = set()
    # with duckdb.connect(args.db_path) as cxn:
    #     for job_id in args.job_id:
    #         rows = cxn.execute(select_dwc, [job_id]).pl()
    #         dwc = rows.rows(named=True)
    #
    #         rows = cxn.execute(select_fields, [job_id]).pl()
    #         fields |= {f["field"] for f in rows.rows(named=True)}
    #
    # raise NotImplementedError
    # select_dwc = f"""
    #     with run as (select * from dwc where dwc_run_id = {args.dwc_run_id})
    #     pivot run on field using first(value) group by ocr_id;
    #     """
    # select_gold = f"""
    #     with run as (select * from gold where gold_run_id = {args.gold_run_id})
    #     pivot run on field using first(value) group by ocr_id;
    #     """
    # select_ocr = """
    #     select distinct ocr_id, ocr_text, image_path from gold join ocr using (ocr_id)
    #     where gold_run_id = ? order by image_path;
    #     """
    #
    # with duckdb.connect(args.db_path) as cxn:
    #     dwc_rows = cxn.execute(select_dwc).pl()
    #     dwc_rows = dwc_rows.rows(named=True)
    #     dwc_rows = {r["ocr_id"]: r for r in dwc_rows}
    #
    #     gold_rows = cxn.execute(select_gold).pl()
    #     gold_rows = gold_rows.rows(named=True)
    #     gold_rows = {r["ocr_id"]: r for r in gold_rows}
    #
    #     ocr_rows = cxn.execute(select_ocr, [args.gold_run_id]).pl()
    #     ocr_rows = ocr_rows.rows(named=True)
    #     ocr_rows = {r["ocr_id"]: r for r in ocr_rows}
    #
    # gold_fields = {
    #     f for f in next(iter(gold_rows.values())) if f not in db_util.GOLD_METADATA
    # }
    #
    # nlp = pipeline.build()
    #
    # # Score
    # fields = sorted(gold_fields)
    # by_field = dict.fromkeys(fields, 0.0)
    # df_data = []
    #
    # ocr_ids = list(ocr_rows.keys())
    # if args.limit:
    #     ocr_ids = ocr_ids[: args.limit]
    #
    # for ocr_id in ocr_ids:
    #     dwc_row = dwc_rows[ocr_id]
    #     gold_row = gold_rows[ocr_id]
    #     ocr_row = ocr_rows[ocr_id]
    #     image_path = Path(ocr_row["image_path"]).name
    #
    #     row1: dict[str, str] = {
    #         "image_path": image_path,
    #         "type": f"gold run {args.gold_run_id}",
    #     }
    #    row2: dict[str, str] = {"image_path": "", "type": f"dwc run {args.dwc_run_id}"}
    #     row3: dict[str, Any] = {"image_path": "", "type": "score"}
    #
    #     for field in fields:
    #         dwc_field = dwc_row[field] or ""
    #         gold_field = gold_row[field] or ""
    #
    #         func = CAS_V1_POST.get(field)
    #         if func and dwc_field:
    #             dwc_field = func(dwc_field, dwc_row, ocr_row["ocr_text"], nlp)
    #
    #         score = Levenshtein.ratio(dwc_field, gold_field)
    #         by_field[field] += score
    #
    #         row1[field] = gold_field
    #         row2[field] = dwc_field
    #         row3[field] = score
    #
    #     df_data.append(row1)
    #     df_data.append(row2)
    #     df_data.append(row3)
    #
    # row: dict[str, Any] = {"image_path": "", "type": "totals"}
    # grand = 0.0
    # for field in fields:
    #     mean = by_field[field] / len(ocr_ids)
    #     grand += mean
    #     row[field] = mean
    # df_data.append(row)
    # grand /= len(fields)
    # df_data.append({"image_path": "", "type": "grand total", fields[0]: grand})
    #
    # if args.results_ods:
    #     df = pd.DataFrame(df_data)
    #     with pd.ExcelWriter(args.results_ods, engine="odf") as writer:
    #         df.to_excel(writer, sheet_name="compare", index=False)


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
    import_parser = subparsers.add_parser(
        "import",
        help="""Import a gold standard from a CSV or JSON file.""",
    )
    import_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )
    import_parser.add_argument(
        "--gold-csv",
        type=Path,
        metavar="PATH",
        help="""Import data from this CSV file.""",
    )
    import_parser.add_argument(
        "--gold-json",
        type=Path,
        metavar="PATH",
        help="""Import data from this JSON file.""",
    )
    import_parser.add_argument(
        "--file-name",
        required=True,
        metavar="COLUMN",
        help="""The file name field used to link OCR records to the gold data.""",
    )
    import_parser.add_argument(
        "--skip",
        action="append",
        metavar="COLUMN",
        help="""Skip this column in the CSV file or field in the JSON field.
            You may use this argument more than once.
            Quote this argument if there are odd characters or spaces in the
            column name.""",
    )
    import_parser.add_argument(
        "--notes", help="""A brief description of the gold standard."""
    )
    import_parser.set_defaults(func=import_action)

    # ------------------------------------------------------------
    score_parser = subparsers.add_parser(
        "score",
        help="""Score a 2 Darwin Core jobs against each other.
            Note: You can only compare fields that are in both jobs against
            OCR IDs that are also in both jobs. So, mismatched columns are
            excluded and mismatched OCR IDs are also excluded.""",
    )
    score_parser.add_argument(
        "--in-csv",
        type=Path,
        required=True,
        help="""Nothing to see here.""",
    )
    # score_parser.add_argument(
    #     "--db-path",
    #     type=Path,
    #     required=True,
    #     metavar="PATH",
    #     help="""Path to the database.""",
    # )
    # score_parser.add_argument(
    #     "--job-id",
    #     type=int,
    #     nargs=2,
    #     help="""The 2 job IDs to compare. Typically one is the gold standard and the
    #         other is the Darwin Core job to compare against the gold standard.""",
    # )
    # score_parser.add_argument(
    #     "--output-csv",
    #     type=Path,
    #     required=True,
    #     metavar="PATH",
    #     help="""Write the results to this CSV file.""",
    # )
    # score_parser.add_argument(
    #     "--limit",
    #     type=int,
    #     help="""Limit the number of records to export.""",
    # )
    score_parser.set_defaults(func=score_action)

    # ------------------------------------------------------------
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    ARGS.func(ARGS)
