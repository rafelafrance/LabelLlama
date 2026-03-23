from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import duckdb

if TYPE_CHECKING:
    from argparse import Namespace


def create_tables(db_path: Path) -> None:
    union = (
        "union(c char, i int, f float, b bool, d double, "
        "cc char[], ii int[], ff float[], dd double[])"
    )

    sql = f"""
        create sequence if not exists job_seq;
        create table if not exists jobs (
            job_id integer primary key default nextval('job_seq'),
            script      char,
            action      char,
            notes       char,
            job_elapsed char,
            job_started timestamptz default current_localtimestamp(),
        );

        create sequence if not exists arg_seq;
        create table if not exists args (
            arg_id integer primary key default nextval('arg_seq'),
            job_id integer, -- references jobs(job_id),
            arg    char,
            value  {union},
        );

        create sequence if not exists doc_seq;
        create table if not exists docs (
            doc_id integer primary key default nextval('doc_seq'),
            job_id      integer, -- references jobs(job_id),
            src_path    char,    -- Path to the source file or image
            src_id      char,    -- An ID in the source file for CSV or JSON etc.
            doc_text    char,    -- The OCRed or imported text
            doc_error   char,    -- OCR error message
            doc_elapsed char,    -- Used to time OCR
        );

        create sequence if not exists field_seq;
        create table if not exists fields (
            field_id integer primary key default nextval('field_seq'),
            job_id   integer, -- references jobs(job_id),
            doc_id   integer, -- references docs(doc_id),
            field    char,
            value    {union},
        );
        """

    with duckdb.connect(db_path) as cxn:
        cxn.execute(sql)


def add_job(
    cxn: duckdb.DuckDBPyConnection,
    script: str,
    args: Namespace | dict | None = None,
    params: dict | None = None,
) -> tuple[int, datetime]:
    args = vars(args) if args else {}
    args |= params or {}

    result = cxn.execute(
        "insert into jobs (script, action, notes) values (?, ?, ?) returning job_id",
        [Path(script).name, args.get("action"), args.get("notes")],
    ).fetchone()
    if not result:
        raise RuntimeError
    job_id = result[0]

    for arg, value in args.items():
        if not isinstance(value, (str, int, float, bool, list)):
            value = str(value)
        cxn.execute(
            "insert into args (job_id, arg, value) values (?, ?, ?)",
            [job_id, arg, value],
        )

    job_started = datetime.now()

    return job_id, job_started


def update_elapsed(
    cxn: duckdb.DuckDBPyConnection, job_id: int | None, job_started: datetime | None
) -> None:
    if job_id is None or job_started is None:
        return
    elapsed = str(datetime.now() - job_started)
    cxn.execute(
        "update jobs set job_elapsed=? where job_id=?",
        [elapsed, job_id],
    )
