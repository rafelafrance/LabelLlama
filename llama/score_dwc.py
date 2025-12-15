#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

import duckdb
import Levenshtein
from rich import print as rprint

from llama.data_formats import specimen_types

HAPPY = 0.9  # Scores above this are green
OK = 0.75  # Scores below this are red


def main(args: argparse.Namespace) -> None:
    if args.display_runs:
        display_runs(args)
    else:
        score_dwc_run(args)


def display_runs(args: argparse.Namespace) -> None:
    with duckdb.connect(args.db_path) as cxn:
        for table in ("gold_run", "dwc_run"):
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


def score_dwc_run(args: argparse.Namespace) -> None:
    spec_type = specimen_types.SPECIMEN_TYPES[args.specimen_type]
    fields = spec_type.output_fields

    by_field = dict.fromkeys(fields, 0.0)

    with duckdb.connect(args.db_path) as cxn:
        sql = r"""
            select columns(gold.*) as "gold_\0",
                   columns(dwc.*)  as "dwc_\0"
              from gold
              join dwc using (pre_dwc_id)
             where gold_run_id = ?
               and dwc_run_id  = ?;
            """
        rows = cxn.execute(sql, [args.gold_run_id, args.dwc_run_id]).pl()
        rows = rows.rows(named=True)

    for row in rows:
        for field in fields:
            gold_val = " ".join(row[f"gold_{field}"])
            dwc_val = " ".join(row[f"dwc_{field}"])

            score = Levenshtein.ratio(gold_val, dwc_val)
            by_field[field] += score

    grand = 0.0
    for field in fields:
        norm = by_field[field] / len(rows)
        grand += norm
        rprint(f"[{get_color(norm)}]{field:>25} {norm:0.2f}")
    grand /= len(fields)
    print()
    rprint(f"[{get_color(grand)}]{'total':>25} {grand:0.2f}")
    print()


def get_color(score: float) -> str:
    color = "green" if score >= HAPPY else "yellow"
    color = color if score >= OK else "red"
    return color


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Score a DwC extraction against a gold standard."""
        ),
    )

    arg_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )

    spec_types = list(specimen_types.SPECIMEN_TYPES.keys())
    arg_parser.add_argument(
        "--specimen-type",
        choices=spec_types,
        default=spec_types[0],
        help="""What type of data is in the json file.""",
    )

    arg_parser.add_argument(
        "--display-runs",
        action="store_true",
        help="""Display gold-run and dwc-run records so you can choose IDs.""",
    )

    arg_parser.add_argument(
        "--gold-run-id",
        type=int,
        help="""Use this gold standard to score against.""",
    )

    arg_parser.add_argument(
        "--dwc-run-id",
        type=int,
        help="""Score this DwC extraction.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
