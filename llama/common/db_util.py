from argparse import Namespace
from datetime import datetime
from pathlib import Path

import duckdb


def create_tables(db_path: Path) -> None:
    sql = """
        create sequence if not exists job_seq;
        create table if not exists job (
            job_id integer primary key default nextval('job_seq'),
            script      char,
            action      char,
            notes       char,
            job_elapsed char,
            job_started timestamptz default current_localtimestamp(),
        );

        create sequence if not exists arg_seq;
        create table if not exists arg (
            arg_id integer primary key default nextval('arg_seq'),
            job_id integer, -- references job(job_id),
            field  char,
            value  char,
        );

        create sequence if not exists ocr_seq;
        create table if not exists ocr (
            ocr_id integer primary key default nextval('ocr_seq'),
            job_id      integer, -- references job(job_id),
            image_path  char,
            ocr_text    char,
            ocr_error   char,
            ocr_elapsed char,
        );

        create sequence if not exists dwc_seq;
        create table if not exists dwc (
            dwc_id integer primary key default nextval('dwc_seq'),
            job_id integer, -- references job(job_id),
            ocr_id integer, -- references ocr(ocr_id),
            field  char,
            value  char,
        );
        """

    with duckdb.connect(db_path) as cxn:
        cxn.execute(sql)


def add_job(
    cxn: duckdb.DuckDBPyConnection,
    script: str,
    args: Namespace | None = None,
    params: dict | None = None,
) -> tuple[int, int]:
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
