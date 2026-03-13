from argparse import Namespace
from datetime import datetime
from pathlib import Path

import duckdb


def create_tables(db_path: Path) -> None:
    sql = """
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
            value  char,
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
            value    char,
        );
        """

    with duckdb.connect(db_path) as cxn:
        cxn.execute(sql)


def add_job(
    cxn: duckdb.DuckDBPyConnection,
    script: str,
    args: Namespace | None = None,
    params: dict | None = None,
) -> tuple[int, datetime]:
    args = vars(args) if args else {}
    args |= params or {}

    script = Path(script).name
    action = args.get("action", "")

    result = cxn.execute(
        """insert into job (script, action) values (?, ?) returning job_id;""",
        [script, action],
    ).fetchone()
    if not result:
        err = "Could not insert new job"
        raise RuntimeError(err)
    job_id = result[0]

    for field, value in args.items():
        cxn.execute(
            """insert into arg (job_id, field, value)
               values (?, ?, ?);""",
            [job_id, field, value],
        )

    job_started = datetime.now()

    return job_id, job_started


def update_elapsed(
    cxn: duckdb.DuckDBPyConnection, job_id: int, job_started: datetime
) -> None:
    elapsed = str(datetime.now() - job_started)
    cxn.execute(
        """update job set elapsed=? where job_id=?;""",
        [elapsed, job_id],
    )
