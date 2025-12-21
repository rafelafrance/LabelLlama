#!/usr/bin/env python3

import argparse
import csv
import textwrap
from pathlib import Path
from typing import Any

import duckdb
import Levenshtein

from llama.modules.dwc_extract import filter_lines, join_lines
from llama.pylib.db_util import get_fields
from llama.signatures.all_signatures import SIGNATURES


class Entry:
    def __init__(
        self, fields: list[str], gold_run: dict[str, Any], gold: dict[str, Any]
    ) -> None:
        self.ocr_id = gold["ocr_id"]
        self.image_name = Path(gold["image_path"]).stem
        self.ocr_text = gold["ocr_text"]
        self.fields = fields

        text = filter_lines(gold["ocr_text"])
        self.text = join_lines(text)

        name = f"gold_{gold_run['gold_run_id']}"
        if gold_run["gold_run_name"]:
            name = gold_run["gold_run_name"]
        self.headers = ["field", name]

        self.table = {"dataset": [name]}
        for field in self.fields:
            self.table[field] = [" ".join(gold[field])]
        self.table["average"] = [""]

    def add_dwc(
        self,
         dwc_run: dict[str, Any],
         dwc: dict[str, Any],
         by_field: dict[str, list[float]],
         idx: int,
    ) -> None:
        self.table["dataset"] += [get_dwc_name(dwc_run), ""]
        avg = 0.0
        for field in self.fields:
            gold = self.table[field][0]
            text = dwc.get(field, [""])
            text = " ".join(text)
            score = Levenshtein.ratio(gold, text)
            avg += score
            self.table[field] += [text, score]
            by_field[field][idx] += score
        avg /= len(self.fields)
        self.table["average"] += ["", avg]


def get_dwc_name(dwc_run: dict[str, Any]) -> str:
    name = f"dwc_{dwc_run['dwc_run_id']}"
    if dwc_run["dwc_run_name"]:
        name = dwc_run["dwc_run_name"]
    return name

def main(args: argparse.Namespace) -> None:
    fields = get_fields(args.signature)

    select_gold = "select * from gold join ocr using (ocr_id) where gold_run_id = ?"
    select_gold_run = "select * from gold_run where gold_run_id = ?"
    select_dwc = "select * from dwc where dwc_run_id = ?"
    select_dwc_run = "select * from dwc_run where dwc_run_id = ?"

    table = {}
    by_field: dict[str, list[float]] = {f: [0.0] * len(args.dwc_run_id) for f in fields}

    with duckdb.connect(args.db_path) as cxn:
        gold_run = cxn.execute(select_gold_run, [args.gold_run_id]).pl()
        gold_run = gold_run.rows(named=True)[0]

        gold = cxn.execute(select_gold, [args.gold_run_id]).pl()
        gold = gold.rows(named=True)

        for gold_ in gold:
            table[gold_["ocr_id"]] = Entry(fields, gold_run, gold_)

        dwc_names = []
        for idx, dwc_run_id in enumerate(args.dwc_run_id):
            dwc_run = cxn.execute(select_dwc_run, [dwc_run_id]).pl()
            dwc_run = dwc_run.rows(named=True)[0]

            dwc_names.append(get_dwc_name(dwc_run))

            dwc = cxn.execute(select_dwc, [dwc_run_id]).pl()
            dwc = {d["ocr_id"]: d for d in dwc.rows(named=True)}

            for entry in table.values():
                if table.get(entry.ocr_id):
                    entry.add_dwc(dwc_run, dwc[entry.ocr_id], by_field, idx)

    with args.csv.open("w") as fh:
        writer = csv.writer(fh)

        writer.writerow(["field", *dwc_names])

        grand = [0.0] * len(args.dwc_run_id)
        for field in fields:
            avg = [b / len(gold) for b in by_field[field]]
            writer.writerow([f"{field} average", *avg])

            for i, a in enumerate(avg):
                grand[i] += a

        grand = [g / len(fields) for g in grand]
        writer.writerow(["global average", *grand])

        for entry in table.values():
            writer.writerow([entry.image_name, entry.ocr_text, "", entry.text, ""])
            for key, value in entry.table.items():
                writer.writerow([key, *value])


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Compare Darwin Core runs to a gold standard."""),
    )

    arg_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )

    arg_parser.add_argument(
        "--gold-run-id",
        type=int,
        required=True,
        help="""Split this gold-run into training, validation, and testing datasets.""",
    )

    arg_parser.add_argument(
        "--dwc-run-id",
        type=int,
        required=True,
        action="append",
        help="""Compare this Darwin Core run to the gold standard.
            You may enter more than one ID.""",
    )

    arg_parser.add_argument(
        "--csv",
        type=Path,
        metavar="PATH",
        help="""Output the report to this CSV file.""",
    )

    sigs = list(SIGNATURES.keys())
    arg_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
