from pathlib import Path

import duckdb

from llama.signatures.all_signatures import SIGNATURES


def get_fields(signature: str) -> list[str]:
    sig = SIGNATURES[signature]
    return sig.output_fields


def get_field_definitions(signature: str) -> str:
    fields = [f"{f} char[]," for f in get_fields(signature)]
    fields = "\n".join(fields)
    return fields


def get_field_names(signature: str) -> str:
    names: str = ", ".join(f"{f}" for f in get_fields(signature))
    return names


def get_field_vars(signature: str) -> str:
    vars_: str = ", ".join(f"${f}" for f in get_fields(signature))
    return vars_


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


def create_dwc_tables(db_path: Path, signature: str) -> None:
    fields = get_field_definitions(signature)

    query = f"""
        create sequence if not exists dwc_run_seq;
        create table if not exists dwc_run (
            dwc_run_id integer primary key default nextval('dwc_run_seq'),
            dwc_run_name  char,
            prompt        char,
            model         char,
            api_host      char,
            notes         char,
            temperature   float,
            max_tokens    integer,
            specimen_type char,
            dwc_run_elapsed char,
            dwc_run_started timestamptz default current_localtimestamp(),
        );

        create sequence if not exists dwc_id_seq;
        create table if not exists dwc (
            dwc_id integer primary key default nextval('dwc_id_seq'),
            dwc_run_id  integer -- references dwc_run(dwc_run_id),
            ocr_id      integer -- references ocr(ocr_id),
            dwc_elapsed char,
            {fields}
        );
        """

    with duckdb.connect(db_path) as cxn:
        cxn.execute(query)


def create_gold_tables(db_path: Path, signature: str) -> None:
    fields = get_field_definitions(signature)

    sql = f"""
        create sequence if not exists gold_run_seq;
        create table if not exists gold_run (
            gold_run_id integer primary key default nextval('gold_run_seq'),
            gold_run_name char,
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
