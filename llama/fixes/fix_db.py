#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

import duckdb

from llama.common import db_util


def fix_action(args: argparse.Namespace) -> None:
    db_util.create_tables(args.new_db)

    with duckdb.connect(args.old_db) as old, duckdb.connect(args.new_db) as new:
        ocr_tables(old, new)
        dwc_tables(old, new)
        gold_tables(old, new)


def gold_tables(old: duckdb.DuckDBPyConnection, new: duckdb.DuckDBPyConnection) -> None:
    gold_runs = old.execute("select * from gold_run").pl()
    gold_runs = gold_runs.rows(named=True)

    for gold_run in gold_runs:
        result = new.execute(
            """
                insert into job (script, action, notes, job_started)
                values (?, ?, ?, ?) returning job_id""",
            [
                "gold_std.py",
                "import",
                gold_run["notes"],
                gold_run["gold_run_created"],
            ],
        ).fetchone()
        if not result:
            raise RuntimeError

        job_id = result[0]

        skips = ("script", "action", "notes", "job_elapsed", "job_started", "signature")
        values = [[job_id, f, v] for f, v in gold_run.items() if f not in skips]
        new.executemany(
            "insert into arg (job_id, field, value) values (?, ?, ?)", values
        )

        golds = old.execute(
            """select ocr_id, field, value from gold where gold_run_id = ?""",
            [gold_run["gold_run_id"]],
        ).pl()
        print(f"{len(golds)=}")
        if len(golds) == 0:
            continue
        golds = golds.rows(named=True)
        values = [[job_id, r["ocr_id"], r["field"], r["value"]] for r in golds]

        new.executemany(
            """insert into dwc (job_id, ocr_id, field, value) values (?, ?, ?, ?)""",
            values,
        )


def dwc_tables(old: duckdb.DuckDBPyConnection, new: duckdb.DuckDBPyConnection) -> None:
    dwc_runs = old.execute("select * from dwc_run").pl()
    dwc_runs = dwc_runs.rows(named=True)

    for dwc_run in dwc_runs:
        result = new.execute(
            """
                insert into job (script, action, notes, job_elapsed, job_started)
                values (?, ?, ?, ?, ?) returning job_id""",
            [
                "run_lm.py",
                "extract",
                dwc_run["notes"],
                dwc_run["dwc_run_elapsed"],
                dwc_run["dwc_run_started"],
            ],
        ).fetchone()
        if not result:
            raise RuntimeError

        job_id = result[0]

        skips = ("script", "action", "notes", "job_elapsed", "job_started")
        values = [[job_id, f, v] for f, v in dwc_run.items() if f not in skips]
        new.executemany(
            "insert into arg (job_id, field, value) values (?, ?, ?)", values
        )

        dwcs = old.execute(
            """select ocr_id, field, value from dwc where dwc_run_id = ?""",
            [dwc_run["dwc_run_id"]],
        ).pl()
        dwcs = dwcs.rows(named=True)
        values = [[job_id, r["ocr_id"], r["field"], r["value"]] for r in dwcs]

        new.executemany(
            """insert into dwc (job_id, ocr_id, field, value) values (?, ?, ?, ?)""",
            values,
        )


def ocr_tables(old: duckdb.DuckDBPyConnection, new: duckdb.DuckDBPyConnection) -> None:
    ocr_runs = old.execute("select * from ocr_run").pl()
    ocr_runs = ocr_runs.rows(named=True)

    for ocr_run in ocr_runs:
        result = new.execute(
            """
                insert into job (script, action, notes, job_elapsed, job_started)
                values (?, ?, ?, ?, ?) returning job_id""",
            [
                "ocr_image.py",
                "ocr",
                ocr_run["notes"],
                ocr_run["ocr_run_elapsed"],
                ocr_run["ocr_run_started"],
            ],
        ).fetchone()
        if not result:
            raise RuntimeError

        job_id = result[0]

        skips = ("script", "action", "notes", "job_elapsed", "job_started")
        values = [[job_id, f, v] for f, v in ocr_run.items() if f not in skips]
        new.executemany(
            "insert into arg (job_id, field, value) values (?, ?, ?)", values
        )

        ocrs = old.execute(
            """
                select ocr_id, image_path, ocr_text, ocr_error, ocr_elapsed
                  from ocr where ocr_run_id = ?""",
            [ocr_run["ocr_run_id"]],
        ).pl()
        ocrs = ocrs.rows(named=True)
        values = [
            [
                job_id,
                r["ocr_id"],
                r["image_path"],
                r["ocr_text"],
                r["ocr_error"],
                r["ocr_elapsed"],
            ]
            for r in ocrs
        ]
        new.executemany(
            """insert into ocr
                    (job_id, ocr_id, image_path, ocr_text, ocr_error, ocr_elapsed)
                    values (?, ?, ?, ?, ?, ?)""",
            values,
        )

    max_ocr_id = old.execute("select max(ocr_id) from ocr").fetchone()
    if not max_ocr_id:
        raise ValueError
    new.execute("drop sequence ocr_seq")
    new.execute(f"create sequence ocr_seq start {max_ocr_id[0] + 1}")


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""OCR images."""),
    )
    subparsers = arg_parser.add_subparsers(
        title="Subcommands",
        description="Actions on gold standard records",
        dest="action",
    )

    # ------------------------------------------------------------
    fix_parser = subparsers.add_parser(
        "fix",
        help="""Fix the database for new schema.""",
    )
    fix_parser.add_argument(
        "--old-db",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the old database.""",
    )
    fix_parser.add_argument(
        "--new-db",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the new database.""",
    )
    fix_parser.set_defaults(func=fix_action)

    # ------------------------------------------------------------
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    ARGS.func(ARGS)
