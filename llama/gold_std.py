#!/usr/bin/env python3

import argparse
import json
import random
import textwrap
from pathlib import Path

import duckdb

from llama.signatures.all_signatures import SIGNATURES, AnySignature


def list_action(args: argparse.Namespace) -> None:
    with duckdb.connect(args.db_path) as cxn:
        for table in ("dwc_run", "gold_run"):
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


def export_action(args: argparse.Namespace) -> None:
    create_gold_tables(args.db_path, args.signature)

    sig: AnySignature = SIGNATURES[args.signature]
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

    with args.gold_json.open("w") as fp:
        json.dump(rows, fp, indent=4)


def import_action(args: argparse.Namespace) -> None:
    create_gold_tables(args.db_path, args.signature)

    with args.gold_json.open() as fp:
        sheets = json.load(fp)

    with duckdb.connect(args.db_path) as cxn:
        run_id = cxn.execute(
            "insert into gold_run (specimen_type, notes, json_path) values (?, ?, ?);",
            [args.signature, args.notes, str(args.json_path)],
        ).fetchone()[0]

        sig = SIGNATURES[args.signature]

        names: str = ", ".join(f"{f}" for f in sig.output_fields)
        vars_: str = ", ".join(f"${f}" for f in sig.output_fields)
        insert_gold = f"""
            insert into gold
                (gold_run_id, ocr_id, {names})
                values ($gold_run_id, $ocr_id, {vars_});
            """

        for sheet in sheets:
            cxn.execute(
                query=insert_gold,
                parameters={
                    "gold_run_id": run_id,
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
            split       char,
            {fields}
        );
        """

    with duckdb.connect(db_path) as cxn:
        cxn.execute(sql)


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

    export_parser.set_defaults(func=export_action)

    # ------------------------------------------------------------
    import_parser = subparsers.add_parser(
        "import",
        help="""Import a gold standard JSON file.""",
    )

    import_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )

    import_parser.add_argument(
        "--gold-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Import data from this JSON file.""",
    )

    sigs = list(SIGNATURES.keys())
    import_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )

    import_parser.set_defaults(func=import_action)

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
    # main(ARGS)
