#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

import duckdb

from llama.common import db_util


def rename_action(args: argparse.Namespace) -> None:
    db_util.create_tables(args.new_db)

    with duckdb.connect(args.new_db) as cxn:
        cxn.execute(f"attach '{args.old_db}' as old")

        jobs = cxn.execute("select * from old.job").pl()
        jobs = jobs.rows(named=True)
        cxn.executemany("""
            insert into jobs (job_id, script, action, notes, job_elapsed, job_started)
            values ($job_id, $script, $action, $notes, $job_elapsed, $job_started)""",
            jobs,
        )
        max_job_id = cxn.execute("select max(job_id) from jobs").fetchone()
        cxn.execute(f"drop sequence job_seq")
        cxn.execute(f"create sequence job_seq start {max_job_id[0] + 1}")

        args = cxn.execute("select * from old.arg").pl()
        args = args.rows(named=True)
        values = [[a["job_id"], a["field"], a["value"]] for a in args]
        cxn.executemany("""
            insert into args (job_id, arg, value)  values (?, ?, ?)""", values
        )

        docs = cxn.execute("select * from old.doc").pl()
        docs = docs.rows(named=True)
        cxn.executemany(
            """
            insert into docs
                (doc_id, job_id, src_path, src_id, doc_text, doc_error, doc_elapsed)
            values
            ($doc_id, $job_id, $src_path, $src_id, $doc_text, $doc_error, $doc_elapsed)
            """,
            docs,
        )
        max_doc_id = cxn.execute("select max(doc_id) from docs").fetchone()
        cxn.execute(f"drop sequence doc_seq")
        cxn.execute(f"create sequence doc_seq start {max_doc_id[0] + 1}")

        fields = cxn.execute("select * from old.dwc").pl()
        fields = fields.rows(named=True)
        values = [[f["job_id"], f["doc_id"], f["field"], f["value"]] for f in fields]
        cxn.executemany(
            """insert into fields (job_id, doc_id, field, value) values (?, ?, ?, ?)""",
            values,
        )


def doc_action(args: argparse.Namespace) -> None:
    with duckdb.connect(args.new_db) as cxn:
        cxn.execute(f"attach '{args.old_db}' as old;")

        cxn.execute("""create table job as select * from old.job""")
        max_job_id = cxn.execute("select max(job_id) from job").fetchone()
        if not max_job_id:
            raise ValueError
        cxn.execute(f"create sequence job_seq start {max_job_id[0] + 1}")

        cxn.execute("""create table arg as select * from old.arg""")
        max_arg_id = cxn.execute("select max(arg_id) from arg").fetchone()
        if not max_arg_id:
            raise ValueError
        cxn.execute(f"create sequence arg_seq start {max_arg_id[0] + 1}")

    db_util.create_tables(args.new_db)

    with duckdb.connect(args.new_db) as cxn:
        cxn.execute(f"attach '{args.old_db}' as old;")

        ocrs = cxn.execute("select * from old.ocr").pl()
        ocrs = ocrs.rows(named=True)
        values = [
            [
                r["ocr_id"],
                r["job_id"],
                r["image_path"],
                r["ocr_text"],
                r["ocr_error"],
                r["ocr_elapsed"],
            ]
            for r in ocrs
        ]
        cxn.executemany(
            """
            insert into doc (doc_id, job_id, src_path, doc_text, doc_error, doc_elapsed)
            values (?, ?, ?, ?, ?, ?)
            """,
            values,
        )
        max_doc_id = cxn.execute("select max(doc_id) from doc").fetchone()
        if not max_doc_id:
            raise ValueError
        cxn.execute("drop sequence doc_seq")
        cxn.execute(f"create sequence doc_seq start {max_doc_id[0] + 1}")

        dwcs = cxn.execute("select * from old.dwc").pl()
        dwcs = dwcs.rows(named=True)
        values = [[r["job_id"], r["ocr_id"], r["field"], r["value"]] for r in dwcs]
        cxn.executemany(
            """
            insert into dwc (job_id, doc_id, field, value) values (?, ?, ?, ?)
            """, values,
        )
        max_dwc_id = cxn.execute("select max(dwc_id) from dwc").fetchone()
        if not max_dwc_id:
            raise ValueError
        cxn.execute("drop sequence dwc_seq")
        cxn.execute(f"create sequence dwc_seq start {max_dwc_id[0] + 1}")


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
            "insert into arg (job_id, field, value) values (?, ?, ?)", values,
        )

        golds = old.execute(
            """select ocr_id, field, value
               from gold
               where gold_run_id = ?""",
            [gold_run["gold_run_id"]],
        ).pl()
        print(f"{len(golds)=}")
        if len(golds) == 0:
            continue
        golds = golds.rows(named=True)
        values = [[job_id, r["ocr_id"], r["field"], r["value"]] for r in golds]

        new.executemany(
            """insert into dwc (job_id, ocr_id, field, value)
               values (?, ?, ?, ?)""",
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
            "insert into arg (job_id, field, value) values (?, ?, ?)", values,
        )

        dwcs = old.execute(
            """select ocr_id, field, value
               from dwc
               where dwc_run_id = ?""",
            [dwc_run["dwc_run_id"]],
        ).pl()
        dwcs = dwcs.rows(named=True)
        values = [[job_id, r["ocr_id"], r["field"], r["value"]] for r in dwcs]

        new.executemany(
            """insert into dwc (job_id, ocr_id, field, value)
               values (?, ?, ?, ?)""",
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
            "insert into arg (job_id, field, value) values (?, ?, ?)", values,
        )

        ocrs = old.execute(
            """
            select ocr_id, image_path, ocr_text, ocr_error, ocr_elapsed
            from ocr
            where ocr_run_id = ?""",
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
        description="Actions to update the database",
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
    doc_parser = subparsers.add_parser(
        "doc",
        help="""Fix the database for importing text directly.""",
    )
    doc_parser.add_argument(
        "--old-db",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the old database.""",
    )
    doc_parser.add_argument(
        "--new-db",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the new database.""",
    )
    doc_parser.set_defaults(func=doc_action)

    # ------------------------------------------------------------
    rename_parser = subparsers.add_parser(
        "rename",
        help="""Rename tables to be plural and adjust column and sequence names.""",
    )
    rename_parser.add_argument(
        "--old-db",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the old database.""",
    )
    rename_parser.add_argument(
        "--new-db",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the new database.""",
    )
    rename_parser.set_defaults(func=rename_action)

    # ------------------------------------------------------------
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    ARGS.func(ARGS)
