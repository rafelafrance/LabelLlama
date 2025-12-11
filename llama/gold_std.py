#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path

import duckdb

from llama.data_formats import specimen_types

ACTIONS: list[str] = ["list", "select", "insert"]


def main(args: argparse.Namespace) -> None:
    if args.action == "list":
        list_dwc_runs(args)

    if args.action == "select":
        select_gold_recs(args)

    if args.action == "insert":
        insert_gold_recs(args)


def list_dwc_runs(args: argparse.Namespace) -> None:
    with duckdb.connect(args.db_path) as cxn:
        rows = cxn.execute("select * from dwc_run").pl()
        rows = rows.rows(named=True)
        for row in rows:
            for key, val in {
                k: v for k, v in row.items() if k not in {"prompt"}
            }.items():
                print(f"{key:>16} {val}")
            print()


def select_gold_recs(args: argparse.Namespace) -> None:
    spec_type = specimen_types.SPECIMEN_TYPES[args.specimen_type]
    names = ", ".join(f"{f}" for f in spec_type.output_fields)

    run_ids = ", ".join(str(i) for i in args.dwc_run_id)
    select = f"""
        select image_path, pre_dwc_text, {names}
            from dwc join pre_dwc using (pre_dwc_id) join ocr using (ocr_id)
            where dwc_run_id in ({run_ids})
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

    create_gold_tables(args.db_path, args.specimen_type)
    run_id = insert_gold_run_rec(args.db_path, args.specimen_type, args.notes)
    insert_gold = create_insert_gold(args.specimen_type)

    spec_type = specimen_types.SPECIMEN_TYPES[args.specimen_type]

    with duckdb.connect(args.db_path) as cxn:
        for sheet in sheets:
            cxn.execute(
                insert_gold,
                {
                    "gold_run_seq": run_id,
                    "pre_dwc_id": sheet["pre_dwc_id"],
                }
                | {n: sheet[n] for n in spec_type.output_fields},
            )


def create_insert_gold(specimen_type: str) -> str:
    spec_type = specimen_types.SPECIMEN_TYPES[specimen_type]

    names = ", ".join(f"{f}" for f in spec_type.output_fields)
    vars_ = ", ".join(f"${f}" for f in spec_type.output_fields)
    insert_gold = f"""
        insert into dwc
            (old_run_id, pre_dwc_id, {names})
            values ($gold_run_id, $pre_dwc_id, {vars_});
        """
    return insert_gold


def insert_gold_run_rec(db_path: Path, specimen_type: str, notes: str) -> int:
    with duckdb.connect(db_path) as cxn:
        run_id = cxn.execute(
            """inseert into gold_run (specimen_type, notes) values (?, ?);""",
            [specimen_type, notes],
        ).fetchone()[0]
    return run_id


def create_gold_tables(db_path: Path, specimen_type: str) -> None:
    # Fields specific to the specimen type
    spec_type = specimen_types.SPECIMEN_TYPES[specimen_type]
    fields = [f"{f} char[]," for f in spec_type.output_fields]
    fields = "\n".join(fields)

    sql = f"""
        create sequence if not exists gold_run_seq;
        create table if not exists gold_run (
            gold_run_id integer primary key default nextval('gold_run_seq'),
            notes         char,
            specimen_type char,
            gold_run_started timestamptz default current_localtimestamp(),
        );

        create sequence if not exists gold_id_seq;
        create table if not exists gold (
            gold_id integer primary key default nextval('gold_id_seq'),
            gold_run_id integer references gold_run(gold_run_id),
            pre_dwc_id  integer references pre_dwc(pre_dwc_id),
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

    spec_types = list(specimen_types.SPECIMEN_TYPES.keys())
    arg_parser.add_argument(
        "--specimen-type",
        choices=spec_types,
        default=spec_types[0],
        help="""What type of data is in the json file.""",
    )

    arg_parser.add_argument(
        "--dwc-run-id",
        type=int,
        action="append",
        help="""Make the gold standard from these dwc-runs.
            You may uses this more than once.""",
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
