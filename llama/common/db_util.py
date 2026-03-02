from pathlib import Path

import duckdb

DWC_METADATA = {"dwc_id", "dwc_run_id", "ocr_id"}
GOLD_METADATA = {"gold_id", "gold_run_id", "ocr_id", "split"}


def create_ocr_tables(db_path: Path) -> None:
    sql = """
        create sequence if not exists ocr_run_seq;
        create table if not exists ocr_run (
            ocr_run_id integer primary key default nextval('ocr_run_seq'),
            prompt          char,
            model           char,
            api_host        char,
            notes           char,
            temperature     float,
            context_length  integer,
            ocr_run_elapsed char,
            ocr_run_started timestamptz default current_localtimestamp(),
        );

        create sequence if not exists ocr_id_seq;
        create table if not exists ocr (
            ocr_id integer primary key default nextval('ocr_id_seq'),
            ocr_run_id   integer, -- references ocr_run(ocr_run_id),
            image_path   char,
            ocr_text     char,
            ocr_error    char,
            ocr_elapsed  char,
        );
        """

    with duckdb.connect(db_path) as cxn:
        cxn.execute(sql)


def create_dwc_tables(db_path: Path) -> None:
    query = """
        create sequence if not exists dwc_run_seq;
        create table if not exists dwc_run (
            dwc_run_id integer primary key default nextval('dwc_run_seq'),
            prompt      char,
            model       char,
            api_host    char,
            signature   char,
            notes       char,
            temperature float,
            max_tokens  integer,
            dwc_run_elapsed char,
            dwc_run_started timestamptz default current_localtimestamp(),
        );

        create sequence if not exists dwc_id_seq;
        create table if not exists dwc (
            dwc_id integer primary key default nextval('dwc_id_seq'),
            dwc_run_id  integer, -- references dwc_run(dwc_run_id),
            ocr_id      integer, -- references ocr(ocr_id),
            field       char,
            value       char,
        );
        """

    with duckdb.connect(db_path) as cxn:
        cxn.execute(query)


def create_gold_tables(db_path: Path) -> None:
    sql = """
        create sequence if not exists gold_run_seq;
        create table if not exists gold_run (
            gold_run_id integer primary key default nextval('gold_run_seq'),
            notes       char,
            src_path    char,
            signature   char,
            gold_run_created timestamptz default current_localtimestamp(),
        );

        create sequence if not exists gold_id_seq;
        create table if not exists gold (
            gold_id integer primary key default nextval('gold_id_seq'),
            gold_run_id integer, -- references gold_run(gold_run_id),
            ocr_id      integer, -- references ocr(ocr_id),
            split       char,
            field       char,
            value       char,
        );
        """

    with duckdb.connect(db_path) as cxn:
        cxn.execute(sql)


def display_runs(db_path: Path, table: str) -> None:
    """Show run information so people can get the right IDs, etc."""
    id_ = f"{table}_id"

    print("=" * 90)
    print(f"{table}\n")

    with duckdb.connect(db_path) as cxn:
        rows = cxn.execute(f"select * from {table}").pl()
        rows = rows.rows(named=True)

        for row in rows:
            for key, value in row.items():
                if key != "prompt":
                    print(f"{key:>30} {value}")

            child = table.removesuffix("_run")

            count = 0
            if id_ and row.get(id_):
                count = cxn.execute(
                    f"select count(*) from {child} where {id_} = ?", [row[id_]]
                ).fetchone()[0]
            print(f"{f'{child} records':>30} {int(count):,d}\n")
