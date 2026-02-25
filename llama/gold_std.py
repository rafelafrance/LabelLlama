#!/usr/bin/env python3

import argparse
import csv
import json
import random
import textwrap
import warnings
from pathlib import Path

import duckdb
import Levenshtein
import pandas as pd

from llama.pylib import db_util
from llama.signatures.all_signatures import SIGNATURES
from llama.signatures.cas_v1 import CAS_V1_POST


def list_action(args: argparse.Namespace) -> None:
    db_util.display_runs(args.db_path, "dwc_run")
    db_util.display_runs(args.db_path, "gold_run")


def init_from_dwc_action(args: argparse.Namespace) -> None:
    db_util.create_dwc_tables(args.db_path)
    db_util.create_gold_tables(args.db_path)

    select = """
        with run as (select * from dwc where dwc_run_id = ?)
        pivot run on field using first(value) group by ocr_id limit ?;
        """

    with duckdb.connect(args.db_path) as cxn:
        rows = cxn.execute(select, [args.dwc_run_id, args.limit]).pl()
        rows = rows.rows(named=True)

    with args.gold_json.open("w") as fp:
        json.dump(rows, fp, indent=4)


def import_json_action(args: argparse.Namespace) -> None:
    db_util.create_gold_tables(args.db_path)

    raise NotImplementedError

    with args.gold_json.open() as fp:
        sheets = json.load(fp)

    with duckdb.connect(args.db_path) as cxn:
        gold_run_id = cxn.execute(
            """
            insert into gold_run (notes, src_path) values (?, ?, ?)
            returning gold_run_id;
            """,
            [args.notes, str(args.gold_json)],
        ).fetchone()[0]

        insert_gold = """
            insert into gold (gold_run_id, ocr_id, split, field, value)
                values ($gold_run_id, $ocr_id, '', $field, $value);
            """

        for sheet in sheets:
            cxn.execute(
                query=insert_gold,
                parameters={
                    "gold_run_id": gold_run_id,
                    "ocr_id": sheet["ocr_id"],
                    "field": None,
                    "value": None,
                },
            )


def import_csv_action(args: argparse.Namespace) -> None:
    db_util.create_gold_tables(args.db_path)

    with args.gold_csv.open() as fp:
        reader = csv.DictReader(fp)
        gold = [dict(r) for r in reader]

    select_ocr = """select image_path, ocr_id from ocr order by ocr_run_id, ocr_id;"""

    with duckdb.connect(args.db_path) as cxn:
        ocr_rows = cxn.execute(select_ocr).pl()
        ocr_rows = ocr_rows.rows(named=True)
        ocr_ids = {Path(r["image_path"]).stem: r["ocr_id"] for r in ocr_rows}

        result = cxn.execute(
            """
            insert into gold_run (notes, src_path, signature) values (?, ?, ?)
            returning gold_run_id;
            """,
            [args.notes, str(args.gold_csv), args.signature],
        ).fetchone()
        gold_run_id = result[0] if result else None

        for row in gold:
            ocr_id = ocr_ids[Path(row[args.file_name]).stem]
            for field, value in row.items():
                if field in args.skip:
                    continue
                cxn.execute(
                    query="""
                        insert into gold (gold_run_id, ocr_id, split, field, value)
                        values ($gold_run_id, $ocr_id, '', $field, $value);
                        """,
                    parameters={
                        "gold_run_id": gold_run_id,
                        "ocr_id": ocr_id,
                        "field": field,
                        "value": value,
                    },
                )


def split_action(args: argparse.Namespace) -> None:
    with duckdb.connect(args.db_path) as cxn:
        query = "select gold_id from gold where gold_run_id = ?"
        df = cxn.execute(query, [args.gold_run_id]).pl()
        rows = df.rows(named=True)

        random.seed(args.seed)
        random.shuffle(rows)

        total: int = len(rows)
        split1: int = round(total * args.train_fract)
        split2: int = split1 + round(total * args.val_fract)

        row_splits: dict[str, list] = {
            "train": rows[:split1],
            "val": rows[split1:split2],
            "test": rows[split2:],
        }

        updates: list[tuple[str, int]] = []
        for split, recs in row_splits.items():
            updates.extend([(split, r["gold_id"]) for r in recs])

        sql = "update gold set split = ? where gold_id = ?"
        cxn.executemany(sql, updates)


def score_dwc_action(args: argparse.Namespace) -> None:
    select_dwc = f"""
        with run as (select * from dwc where dwc_run_id = {args.dwc_run_id})
        pivot run on field using first(value) group by ocr_id;
        """
    select_gold = f"""
        with run as (select * from gold where gold_run_id = {args.gold_run_id})
        pivot run on field using first(value) group by ocr_id;
        """
    select_ocr = """
        select distinct ocr_id, ocr_text, image_path from gold join ocr using (ocr_id)
        where gold_run_id = ? order by image_path;
        """

    with duckdb.connect(args.db_path) as cxn:
        dwc_rows = cxn.execute(select_dwc).pl()
        dwc_rows = dwc_rows.rows(named=True)
        dwc_rows = {r["ocr_id"]: r for r in dwc_rows}

        gold_rows = cxn.execute(select_gold).pl()
        gold_rows = gold_rows.rows(named=True)
        gold_rows = {r["ocr_id"]: r for r in gold_rows}

        ocr_rows = cxn.execute(select_ocr, [args.gold_run_id]).pl()
        ocr_rows = ocr_rows.rows(named=True)
        ocr_rows = {r["ocr_id"]: r for r in ocr_rows}

    # Validate fields
    dwc_fields = {
        f for f in next(iter(dwc_rows.values())) if f not in db_util.DWC_METADATA
    }
    gold_fields = {
        f for f in next(iter(gold_rows.values())) if f not in db_util.GOLD_METADATA
    }
    fields = dwc_fields & gold_fields
    if dwc_fields != gold_fields:
        extra_dwc = sorted(dwc_fields - gold_fields)
        extra_gold = sorted(gold_fields - dwc_fields)
        warnings.warn(
            "The Darwin Core and gold standard field lists are not the same. "
            "The Darwin Core has these extra fields "
            f"{' '.join(extra_dwc) if extra_dwc else 'None'} "
            " and the gold standard has these "
            f"{' '.join(extra_gold) if extra_gold else 'None'} fields.",
            stacklevel=1,
        )

    # Validate OCR IDs
    dwc_ocr_ids = set(dwc_rows)
    gold_ocr_ids = set(gold_rows)
    ocr_ids = dwc_ocr_ids & gold_ocr_ids
    if dwc_ocr_ids != gold_ocr_ids:
        warnings.warn(
            f"The gold standard has {len(gold_ocr_ids)} records and the DwC has "
            f"{len(dwc_ocr_ids)} records.",
            stacklevel=1,
        )

    # Score
    fields = sorted(fields)
    ocr_ids = sorted(ocr_ids)
    by_field = dict.fromkeys(fields, 0.0)
    df_data = []

    for ocr_id in ocr_ids:
        dwc_row = dwc_rows[ocr_id]
        gold_row = gold_rows[ocr_id]
        ocr_info = ocr_rows[ocr_id]
        image_path = Path(ocr_info["image_path"]).name

        row1 = {"image_path": image_path, "type": f"gold run {args.gold_run_id}"}
        row2 = {"image_path": "", "type": f"dwc run {args.dwc_run_id}"}
        row3 = {"image_path": "", "type": "score"}

        for field in fields:
            gold_val = gold_row[field] or ""

            dwc_val = dwc_row[field] or ""
            if func := CAS_V1_POST.get(field):
                dwc_val = func(dwc_val, ocr_info["ocr_text"])

            score = Levenshtein.ratio(dwc_val, gold_val)
            by_field[field] += score

            row1[field] = gold_val
            row2[field] = dwc_val
            row3[field] = score

        df_data.append(row1)
        df_data.append(row2)
        df_data.append(row3)

    row = {"image_path": "", "type": "totals"}
    grand = 0.0
    for field in fields:
        mean = by_field[field] / len(ocr_ids)
        grand += mean
        row[field] = mean
    df_data.append(row)
    grand /= len(fields)
    df_data.append({"image_path": "", "type": "grand total", fields[0]: grand})

    if args.results_ods:
        df = pd.DataFrame(df_data)
        with pd.ExcelWriter(args.results_ods, engine="odf") as writer:
            df.to_excel(writer, sheet_name="compare", index=False)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Manipulate annotated specimen metadata."""),
    )

    subparsers = arg_parser.add_subparsers(
        title="Subcommands", description="Actions on gold standard records"
    )

    # ------------------------------------------------------------
    list_parser = subparsers.add_parser(
        "list",
        help="""List data to help you decide which DwC run to use as a basis for a
            gold standard.""",
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
    init_from_dwc_parser = subparsers.add_parser(
        "init-from-dwc",
        help="""Create a new starter gold standard from a DwC run. It is often easier
            to modify an existing gold standard than create a new one. You can update
            the annotations using the annotate_fields.py utility.""",
    )
    init_from_dwc_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )
    init_from_dwc_parser.add_argument(
        "--gold-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Export the data to this JSON file.""",
    )
    init_from_dwc_parser.add_argument(
        "--dwc-run-id",
        type=int,
        required=True,
        help="""Make a gold standard template from this dwc-run.
            Note: It's only using the dwc-run as a starter not the data itself.""",
    )
    init_from_dwc_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the number of records to export.""",
    )
    init_from_dwc_parser.set_defaults(func=init_from_dwc_action)

    # ------------------------------------------------------------
    # import_json_parser = subparsers.add_parser(
    #     "import-json",
    #     help="""Import a gold standard JSON file. These typically come from
    #         the annotate_gold.py utility.""",
    # )
    # import_json_parser.add_argument(
    #     "--db-path",
    #     type=Path,
    #     required=True,
    #     metavar="PATH",
    #     help="""Path to the database.""",
    # )
    # import_json_parser.add_argument(
    #     "--gold-json",
    #     type=Path,
    #     required=True,
    #     metavar="PATH",
    #     help="""Import data from this JSON file.""",
    # )
    # import_json_parser.add_argument(
    #     "--skip",
    #     action="append",
    #     metavar="COLUMN",
    #     help="""Skip this column in the CSV file. You may use this argument more than
    #         once. Quote this argument if there are odd characters or spaces in the
    #         column name.""",
    # )
    # import_json_parser.add_argument(
    #     "--notes", help="""A breif description of the gold standard."""
    # )
    # import_json_parser.set_defaults(func=import_json_action)

    # ------------------------------------------------------------
    import_csv_parser = subparsers.add_parser(
        "import-csv",
        help="""Import a gold standard CSV file. These typically come from
            outside sources.""",
    )
    import_csv_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )
    import_csv_parser.add_argument(
        "--gold-csv",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Import data from this CSV file.""",
    )
    import_csv_parser.add_argument(
        "--file-name",
        required=True,
        metavar="COLUMN",
        help="""The file name column used to link OCR records.""",
    )
    sigs = list(SIGNATURES.keys())
    list_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )
    import_csv_parser.add_argument(
        "--skip",
        action="append",
        metavar="COLUMN",
        help="""Skip this column in the CSV file. You may use this argument more than
            once. Quote this argument if there are odd characters or spaces in the
            column name.""",
    )
    import_csv_parser.add_argument(
        "--notes", help="""A breif description of the gold standard."""
    )
    import_csv_parser.set_defaults(func=import_csv_action)

    # ------------------------------------------------------------
    score_dwc_parser = subparsers.add_parser(
        "score-dwc",
        help="""Score a Darwin Core run against a gold standard.""",
    )
    score_dwc_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )
    score_dwc_parser.add_argument(
        "--dwc-run-id",
        type=int,
        required=True,
        help="""Score this Darwin Core run.""",
    )
    score_dwc_parser.add_argument(
        "--gold-run-id",
        type=int,
        required=True,
        help="""Use this gold standard to score against.""",
    )
    score_dwc_parser.add_argument(
        "--results-ods",
        type=Path,
        metavar="PATH",
        help="""Write the results to this spreadsheet.""",
    )
    score_dwc_parser.set_defaults(func=score_dwc_action)

    # ------------------------------------------------------------
    split_parser = subparsers.add_parser(
        "split", help="Split a gold_run into training, validation, and test datasets"
    )
    split_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )
    split_parser.add_argument(
        "--gold-run-id",
        type=int,
        required=True,
        help="""Split this gold-run into training, validation, and testing datasets.""",
    )
    split_parser.add_argument(
        "--train-fract",
        type=float,
        default=0.1,
        metavar="FLOAT",
        help="""What fraction of the records to use for training.
            (default: %(default)s)""",
    )
    split_parser.add_argument(
        "--val-fract",
        type=float,
        default=0.5,
        metavar="FLOAT",
        help="""What fraction of the records to use for valiation.
            (default: %(default)s)""",
    )
    split_parser.add_argument(
        "--seed",
        type=int,
        default=992583,
        help="""Seed for the random number generator. (default: %(default)s)""",
    )
    split_parser.set_defaults(func=split_action)

    # ------------------------------------------------------------

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    ARGS.func(ARGS)
