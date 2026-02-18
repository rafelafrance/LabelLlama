#!/usr/bin/env python3

import argparse
import csv
import json
import random
import textwrap
from pathlib import Path

import duckdb

from llama.pylib import db_util
from llama.signatures.all_signatures import SIGNATURES


def list_action(args: argparse.Namespace) -> None:
    db_util.display_runs(args.db_path, "dwc_run")
    db_util.display_runs(args.db_path, "gold_run")


def export_action(args: argparse.Namespace) -> None:
    db_util.create_gold_tables(args.db_path, args.signature)
    fields = db_util.get_field_names(args.signature)

    select = f"""
        select image_path, ocr_id, ocr_text, {fields}
            from dwc_{args.signature} join ocr using (ocr_id)
            where dwc_run_id = ? limit ?
        """

    with duckdb.connect(args.db_path) as cxn:
        rows = cxn.execute(select, [args.dwc_run_id, args.limit]).pl()
        rows = rows.rows(named=True)

    with args.gold_json.open("w") as fp:
        json.dump(rows, fp, indent=4)


def import_json_action(args: argparse.Namespace) -> None:
    db_util.create_gold_tables(args.db_path, args.signature)

    with args.gold_json.open() as fp:
        sheets = json.load(fp)

    with duckdb.connect(args.db_path) as cxn:
        gold_run_id = cxn.execute(
            """
            insert into gold_run (specimen_type, notes, src_path) values (?, ?, ?)
            returning gold_run_id;
            """,
            [args.signature, args.notes, str(args.gold_json)],
        ).fetchone()[0]

        names: str = db_util.get_field_names(args.signature)
        vars_: str = db_util.get_field_vars(args.signature)
        insert_gold = f"""
            insert into gold_{args.signature}
                (gold_run_id, ocr_id, {names})
                values ($gold_run_id, $ocr_id, {vars_});
            """

        sig = SIGNATURES[args.signature]

        for sheet in sheets:
            cxn.execute(
                query=insert_gold,
                parameters={
                    "gold_run_id": gold_run_id,
                    "ocr_id": sheet["ocr_id"],
                }
                | {n: sheet[n] for n in sig.output_fields},
            )


def import_csv_action(args: argparse.Namespace) -> None:
    db_util.create_gold_tables(args.db_path, args.signature)

    with args.gold_csv.open() as fp:
        reader = csv.DictReader(fp)
        sheets = [dict(r) for r in reader]

    with duckdb.connect(args.db_path) as cxn:
        gold_run_id = cxn.execute(
            """
            insert into gold_run (specimen_type, notes, src_path) values (?, ?, ?)
            returning gold_run_id;
            """,
            [args.signature, args.notes, str(args.gold_csv)],
        ).fetchone()[0]

        names: str = db_util.get_field_names(args.signature)
        vars_: str = db_util.get_field_vars(args.signature)
        insert_gold = f"""
            insert into gold_{args.signature}
                (gold_run_id, ocr_id, {names})
                values ($gold_run_id, $ocr_id, {vars_});
            """

        sig = SIGNATURES[args.signature]

        for sheet in sheets:
            cxn.execute(
                query=insert_gold,
                parameters={
                    "gold_run_id": gold_run_id,
                    "ocr_id": sheet["ocr_id"],
                }
                | {n: sheet[n] for n in sig.output_fields},
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
    export_parser = subparsers.add_parser(
        "export",
        help="""Export this DwC run data as a starting point for a new gold standard.
            This will create a JSON file that you can feed into annotate_gold GUI
            script.""",
    )

    export_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )

    export_parser.add_argument(
        "--gold-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Export the data to this JSON file.""",
    )

    export_parser.add_argument(
        "--dwc-run-id",
        type=int,
        required=True,
        help="""Make a gold standard template from this dwc-run.
            Note: It's only using the dwc-run as a starter not the data itself.""",
    )

    sigs = list(SIGNATURES.keys())
    export_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the number of records to export.""",
    )

    export_parser.set_defaults(func=export_action)

    # ------------------------------------------------------------
    import_json_parser = subparsers.add_parser(
        "import-json",
        help="""Import a gold standard JSON file.""",
    )

    import_json_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )

    import_json_parser.add_argument(
        "--gold-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Import data from this JSON file.""",
    )

    sigs = list(SIGNATURES.keys())
    import_json_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )

    import_json_parser.add_argument(
        "--notes", help="""A breif description of the gold standard."""
    )

    import_json_parser.set_defaults(func=import_json_action)

    # ------------------------------------------------------------
    import_csv_parser = subparsers.add_parser(
        "import-csv",
        help="""Import a gold standard CSV file.""",
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

    sigs = list(SIGNATURES.keys())
    import_csv_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )

    import_csv_parser.add_argument(
        "--notes", help="""A breif description of the gold standard."""
    )

    import_csv_parser.set_defaults(func=import_csv_action)

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
