#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path

import duckdb

from llama.signatures.all_signatures import SIGNATURES

ACTIONS: list[str] = ["list", "select", "insert"]


def main(args: argparse.Namespace) -> None:
    create_gold_tables(args.db_path, args.specimen_type)

    if args.action == "list":
        list_dwc_runs(args)

    if args.action == "select":
        select_gold_recs(args)

    if args.action == "insert":
        insert_gold_recs(args)


def list_dwc_runs(args: argparse.Namespace) -> None:
    with duckdb.connect(args.db_path) as cxn:
        for table in ("pre_dwc_run", "dwc_run", "gold_run"):
            child = table.removesuffix("_run")
            id_ = f"{table}_id"

            print("=" * 90)
            print(f"{table}\n")

            rows = cxn.execute(f"select * from {table}").pl()
            rows = rows.rows(named=True)
            for row in rows:
                for key, val in {
                    k: v for k, v in row.items() if k not in {"prompt"}
                }.items():
                    print(f"{key:>20} {val}")

                count = cxn.execute(
                    f"select count(*) from {child} where {id_} = ?", [row[id_]]
                ).fetchone()[0]
                print(f"{'number of records':>20} {count}")

                print()


def select_gold_recs(args: argparse.Namespace) -> None:
    sig = SIGNATURES[args.signature]
    names = ", ".join(f"{f}" for f in sig.output_fields)

    select = f"""
        select image_path, ocr_id, ocr_text, {names}
            from dwc join ocr using (ocr_id)
            where ocr_id = {args.ocr_id}
        """
    if args.limit:
        select += f" limit {args.limit}"

    with duckdb.connect(args.db_path) as cxn:
        rows = cxn.execute(select).pl()
        rows = rows.rows(named=True)

    with args.gold_json.open("w") as f:
        json.dump(rows, f, indent=4)


def insert_gold_recs(args: argparse.Namespace) -> None:
    with args.gold_json.open() as f:
        sheets = json.load(f)

    run_id = insert_gold_run_rec(
        args.db_path, args.specimen_type, args.notes, args.gold_json
    )
    insert_gold = create_insert_gold(args.specimen_type)

    sig = SIGNATURES[args.signature]

    with duckdb.connect(args.db_path) as cxn:
        for sheet in sheets:
            cxn.execute(
                insert_gold,
                {
                    "gold_run_id": run_id,
                    "ocr_id": sheet["ocr_id"],
                }
                | {n: sheet[n] for n in sig.output_fields},
            )


def create_insert_gold(signature: str) -> str:
    sig = SIGNATURES[signature]

    names = ", ".join(f"{f}" for f in sig.output_fields)
    vars_ = ", ".join(f"${f}" for f in sig.output_fields)
    insert_gold = f"""
        insert into gold
            (gold_run_id, ocr_id, {names})
            values ($gold_run_id, $ocr_id, {vars_});
        """
    return insert_gold


def insert_gold_run_rec(
    db_path: Path, specimen_type: str, notes: str, json_path: Path
) -> int:
    with duckdb.connect(db_path) as cxn:
        run_id = cxn.execute(
            "insert into gold_run (specimen_type, notes, json_path) values (?, ?, ?);",
            [specimen_type, notes, str(json_path)],
        ).fetchone()[0]
    return run_id


def create_gold_tables(db_path: Path, signature: str) -> None:
    # Fields specific to the specimen type
    sig = SIGNATURES[signature]
    fields = [f"{f} char[]," for f in sig.output_fields]
    fields = "\n".join(fields)

    sql = f"""
        create sequence if not exists gold_run_seq;
        create table if not exists gold_run (
            gold_run_id integer primary key default nextval('gold_run_seq'),
            notes         char,
            specimen_type char,
            json_path     char,
            gold_run_created timestamptz default current_localtimestamp(),
        );

        create sequence if not exists gold_id_seq;
        create table if not exists gold (
            gold_id integer primary key default nextval('gold_id_seq'),
            gold_run_id integer, -- references gold_run(gold_run_id),
            ocr_id      integer, -- references ocr(ocr_id),
            {fields}
        );
        """

    with duckdb.connect(db_path) as cxn:
        cxn.execute(sql)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Read and write the annotated specimen metadata to/from a JSON file."""
        ),
    )

    arg_parser.add_argument(
        "--action",
        choices=ACTIONS,
        default=ACTIONS[0],
        help="""What to do, select from DB to JSON or insert from JSON to DB.""",
    )

    arg_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )

    arg_parser.add_argument(
        "--gold-json",
        type=Path,
        metavar="PATH",
        help="""Work with this JSON file.""",
    )

    sigs = list(SIGNATURES.keys())
    arg_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )

    arg_parser.add_argument(
        "--dwc-run-id",
        type=int,
        help="""Make a gold standard template from this dwc-run.
            Note: It's only using the dwc-run as a starter not the data itself.""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        help="""Notes about this dataset.""",
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
    main(ARGS)
