#!/usr/bin/env python3
"""
Compare LLM outputs from different models against each other & choose a winner.

Getting a decent gold standard is nearly impossible. People are inconsistent in how the
data should be formatted (capitalization, punctuation, normalization, etc.). And that is
if you can get any one to try. I always wind up fixing the gold standard. Given that,
I am trying to get good training data other ways. This attempt is to run the same label
thru several different models and see what is the most common answer. Of course there
are many issues with this approach too, like using the same model architecture and
believing that the similarity is telling us something. And so on. Nevertheless, I am
trying this because I really really need training data.

I am going to mark the most common parse value, if there is one. I will allow you to
limit the most common value to a majority. Obviously, you need at least 3 models run
against the same text to be useful.

Output format: more or less
    Index: <row_group>.<column>.<llm_index>

| Text | Source  | Row group | Type    |  Column 1   |  Column 2   | ... |  Column n   |
|------|---------|-----------|---------|-------------|-------------| ... |-------------|
|      |         |           | llm 1   | value 1.1.1 | value 1.2.1 | ... | value 1.n.1 |
| text | /path/1 |     1     | llm 2   | value 1.1.2 | value 1.2.2 | ... | value 1.n.2 |
|      |         |           | llm 3   | value 1.1.3 | value 1.2.3 | ... | value 1.n.3 |
|      |         |           | winner  | winner1.1.3 | winner1.2.3 | ... | winner1.n.3 |
|------|---------|-----------|---------|-------------|-------------| ... |-------------|
|      |         |           | llm 1   | value 2.1.1 | value 2.2.1 | ... | value 2.n.1 |
| text | /path/2 |     2     | llm 2   | value 2.2.1 | value 2.2.2 | ... | value 2.n.2 |
|      |         |           | llm 3   | score 2.1.3 | score 2.2.3 | ... | score 2.n.3 |
|      |         |           | winner  | winner2.1.3 | winner2.2.3 | ... | winner2.n.3 |
"""

import argparse
import logging
import textwrap
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from llama.pylib import log

FIRST_COLUMNS = ["text", "source", "row_group", "row_type"]


@dataclass
class RowGroup:
    first_columns: dict[str, str] = field(default_factory=dict)
    parse_rows: list[dict[str, str]] = field(default_factory=list)
    winner_row: dict[str, Any] = field(default_factory=dict)

    def flatten(self) -> list[dict]:
        rows = [self.first_columns | row for row in self.parse_rows]
        rows += [self.first_columns | self.winner_row]
        return rows


def compare_model_winner(args: argparse.Namespace) -> None:
    """Compare LLM outputs against each other and choose a winner."""
    job_began = log.job_began(args.log_file, args=args)

    # Read OCR data
    ocr_df = pd.read_csv(args.ocr_file, dtype=str).fillna("")
    ocr_by_image = {o["source"]: o for o in ocr_df.to_dict("records")}

    # Init 2 of the 3 indexes for the quasi 3D struct, see this script's doc string
    image_paths = set(ocr_by_image)
    column_keys = {}

    # Get parsed data
    parsed_data = {}
    for parse_file in args.parse_file:
        llm_df = pd.read_csv(parse_file, dtype=str).fillna("")
        column_keys |= dict.fromkeys(llm_df.columns)
        image_paths &= set(llm_df["source"])

        llm_list = llm_df.to_dict("records")
        parsed_data[parse_file.stem] = {r["source"]: r for r in llm_list}

    # Finish building the row index
    image_paths = sorted(image_paths)
    image_paths = image_paths[: args.limit]
    logging.info(f"Reporting on {len(image_paths)} images")

    # Get common columns in the original order
    columns = [k for k in column_keys if k not in FIRST_COLUMNS]

    tally = defaultdict(lambda: {p.stem: 0 for p in args.parse_file})
    row_groups = []
    for i, image_path in enumerate(image_paths, 1):
        group = RowGroup(
            first_columns={
                "text": ocr_by_image[image_path]["text"],
                "image_path": image_path,
                "row_group": str(i),
            }
        )
        # Build parse rows
        for parse_file in args.parse_file:
            stem = parse_file.stem
            row = parsed_data[stem][image_path]
            group.parse_rows.append(
                {"row_type": stem, **{c: row.get(c, "") for c in columns}}
            )

        # Get the winners
        for col in columns:
            values = defaultdict(list)
            for row in group.parse_rows:
                values[row[col]].append(row["row_type"])
            counts = sorted(values.items(), key=lambda v: len(v[1]))
            winner = counts[0]
            result = winner[0]
            if len(counts) > 1 and len(winner[1]) == len(counts[1][1]):
                result = "<no_winner>"
            if args.majority and float(len(winner[1])) < len(values) / 2.0:
                result = "<no_winner>"
            result = result or "<empty>"
            group.winner_row[col] = result
            if result != "<no_winner>":
                for w in winner[1]:
                    tally[col][w] += 1

        row_groups.append(group)

    rows = []
    for group in row_groups:
        rows += group.flatten()

    detail_df = pd.DataFrame(rows)

    totals: dict[str, dict[str, Any]] = {
        f.stem: {"row_group": "Total", "row_type": f.stem, "average": 0.0}
        for f in args.parse_file
    }
    for col, counts in tally.items():
        for stem, count in counts.items():
            totals[stem][col] = count / len(image_paths)
            totals[stem]["average"] += totals[stem][col]
    for counts in totals.values():
        counts["average"] /= len(tally)

    summary_df = pd.DataFrame(totals.values())

    with pd.ExcelWriter(args.output_ods, engine="odf") as writer:
        detail_df.to_excel(writer, sheet_name="detail", index=False)
        summary_df.to_excel(writer, sheet_name="summary", index=False)

    log.job_elapsed(job_began)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
            Compare the outputs of language model extracts against each other.
            Sometimes you don't have a gold standard or GBIF data and yet you
            still want to compare language model (LM) outputs. This prints the
            outputs and keeps track of how often each model agrees with the other
            models. WARNING: This is a VERY WEAK scoring method. You've been warned.
            I use it mostly for visually inspecting model outputs.
            """,
        ),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--ocr-file",
        type=Path,
        required=True,
        metavar="path",
        help="""This file contains the original OCRed text.""",
    )
    io_group.add_argument(
        "--parse-file",
        type=Path,
        required=True,
        action="append",
        metavar="path",
        help="""The cleaned LLM parse file. You may compare several files at once.""",
    )
    io_group.add_argument(
        "--output-ods",
        type=Path,
        required=True,
        metavar="path",
        help="""Write the comparison results to this spreadsheet.""",
    )
    winner_group = arg_parser.add_argument_group("Majority options")
    winner_group.add_argument(
        "--majority",
        action="store_true",
        help="""Only report the a majority result as the winner.""",
    )
    logging_group = arg_parser.add_argument_group("logging options")
    logging_group.add_argument(
        "--log-file",
        type=Path,
        metavar="path",
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    logging_group.add_argument(
        "--notes",
        metavar="string",
        help="""Notes for logging.""",
    )
    debugging_group = arg_parser.add_argument_group("debugging options")
    debugging_group.add_argument(
        "--limit",
        type=int,
        metavar="int",
        help="""Limit to this many row groups.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    compare_model_winner(ARGS)
