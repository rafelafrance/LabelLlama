#!/usr/bin/env python3
"""
Preprocess OCR text to make information extraction easier.

Note:
`export  POLARS_IMPORT_INTERVAL_AS_STRUCT=1`
before running this script.

"""

import argparse
import re
import textwrap
from pathlib import Path

import duckdb
from tqdm import tqdm

EXCLUDE = [
    "academy",
    "botanical",
    "center for",
    "forest service",
    "herbaria",
    "herbarium",
    "plant biology",
    "sciences",
    "university",
]
EXCLUDE = [rf"\b{e}\b" for e in EXCLUDE]

REMOVE_LN = re.compile(f"({'|'.join(EXCLUDE)})", flags=re.IGNORECASE)


def pre_dwc(args: argparse.Namespace) -> None:
    """Preprocess OCR text."""
    create_pre_dwc_tables(args.db_path)

    with duckdb.connect(args.db_path) as cxn:
        run_id = cxn.execute(
            """
            insert into pre_dwc_run (notes) values (?) returning pre_dwc_run_id;
            """,
            [args.notes.strip()],
        ).fetchone()[0]

        ocr_rows = select_records(args.db_path, args.ocr_run_id, args.limit)
        ocr_rows = ocr_rows.rows(named=True)
        for ocr_row in tqdm(ocr_rows):
            text = ocr_row["ocr_text"]

            text = filter_lines(text)
            text = join_lines(text)

            cxn.execute(
                """
                insert into pre_dwc
                    (pre_dwc_run_id, ocr_id, pre_dwc_text)
                    values (?, ?, ?);
                """,
                [run_id, ocr_row["ocr_id"], text],
            )


def join_lines(text: str) -> str:
    text = text.replace("\n\n", "<br>")
    text = text.replace("\n", " ")
    text = text.replace("<br>", "\n")
    return text


def filter_lines(text: str) -> str:
    lines = [ln for ln in text.splitlines() if not REMOVE_LN.search(ln)]
    text = "\n".join(lines)
    return text


def select_records(
    db_path: Path, ocr_run_id: list[int], limit: int | None = None
) -> list:
    run_ids = ", ".join(str(i) for i in ocr_run_id)
    sql = f"select * from ocr where ocr_run_id in ({run_ids}) and ocr_text <> ''"
    if limit:
        sql += f" limit {limit}"

    with duckdb.connect(db_path) as cxn:
        return cxn.execute(sql).pl()


def create_pre_dwc_tables(db_path: Path) -> None:
    sql = """
        create sequence if not exists pre_dwc_run_seq;
        create table if not exists pre_dwc_run (
            pre_dwc_run_id integer primary key default nextval('pre_dwc_run_seq'),
            notes          char,
            pre_dwc_run_started timestamptz default current_localtimestamp(),
        );

        create sequence if not exists pre_dwc_id_seq;
        create table if not exists pre_dwc (
            pre_dwc_id integer primary key default nextval('pre_dwc_id_seq'),
            pre_dwc_run_id integer references pre_dwc_run(pre_dwc_run_id),
            ocr_id         integer references ocr(ocr_id),
            pre_dwc_text   char,
        );
        """

    with duckdb.connect(db_path) as cxn:
        cxn.execute(sql)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""OCR all images in a directory."""),
    )

    arg_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )

    arg_parser.add_argument(
        "--ocr-run-id",
        type=int,
        required=True,
        action="append",
        help="""Parse records from this OCR run. You may uses this more than once.""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the number of records to parse?""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        help="""Notes about this dataset.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    pre_dwc(ARGS)
