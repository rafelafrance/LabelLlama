#!/usr/bin/env python3
"""
Compare LLM outputs against a gold standard.

Output format: more or less
    Index: <row_group>.<column>.<llm_index>

| Text | Source  | Row group | Type    |  Column 1   |  Column 2   | ... |  Column n   |
|------|---------|-----------|---------|-------------|-------------| ... |-------------|
|      |         |           | gold    | gold  1.1   | gold  1.2   | ... | gold  1.n   |
|      |         |           | llm 1   | value 1.1.1 | value 1.2.1 | ... | value 1.n.1 |
| text | /path/1 |     1     | llm 2   | value 1.1.2 | value 1.2.2 | ... | value 1.n.2 |
|      |         |           | score 1 | score 1.1.1 | score 1.2.1 | ... | score 1.n.1 |
|      |         |           | score 2 | score 1.1.2 | score 1.2.2 | ... | score 1.n.2 |
|------|---------|-----------|---------|-------------|-------------| ... |-------------|
|      |         |           | gold    | gold  2.1   | gold  2.2   | ... | gold  2.n   |
|      |         |           | llm 1   | value 2.1.1 | value 2.2.1 | ... | value 2.n.1 |
| text | /path/2 |     2     | llm 2   | value 2.2.1 | value 2.2.2 | ... | value 2.n.2 |
|      |         |           | score 1 | score 2.1.1 | score 2.2.1 | ... | score 2.n.1 |
|      |         |           | score 2 | score 2.2.1 | score 2.2.2 | ... | score 2.n.2 |
"""

import argparse
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from llama.fields.base_field import BaseField
from llama.pylib import log, prompt_util

FIRST_COLUMNS = ["text", "source", "row_group", "row_type"]


@dataclass
class Score:
    score: float = 0.0
    method: str = ""


@dataclass
class RowGroup:
    """
    A group of rows that get displayed together.

    The entire group is indexed by the image source. So, for each OCRed image or other
    source like CSV we have:
        - The "first" columns. Which are handled differently, see above.
        - A golden row with the expected values for each image.
        - A set of LLM runs against the OCRed data. Each run tries a different model,
          or other parameters in an attempt to get as close to the expected golden
          values as possible.
        - A set of scores for each LLM run. How well did the model actually do?
    """

    first_columns: dict[str, str] = field(default_factory=dict)
    gold_row: dict = field(default_factory=dict)
    parse_rows: list[dict] = field(default_factory=list)
    score_rows: list[dict] = field(default_factory=list)

    def flatten(self) -> list[dict]:
        rows = [self.first_columns | self.gold_row]
        rows += [self.first_columns | row for row in self.parse_rows]
        rows += [self.first_columns | row for row in self.score_rows]
        return rows


def score_against_gold(args: argparse.Namespace) -> None:
    """
    Compare LLM outputs against a gold standard and write an HTML report.

    I'm building table with groups of rows. Each group of rows is indexed by
    the image source (its path).
    """
    log.started(args.log_file, args=args)

    # Read OCR data
    ocr_df = pd.read_csv(args.ocr_file, dtype=str).fillna("")
    ocr_by_image = {o["source"]: o for o in ocr_df.to_dict("records")}

    # Read Gold data
    gold_df = pd.read_csv(args.gold_file, dtype=str).fillna("")
    gold_by_image = {g["source"]: g for g in gold_df.to_dict("records")}

    # Init row and column indexes
    image_paths = set(gold_by_image)
    columns = dict.fromkeys(gold_by_image)

    # Get parsed data
    parsed_data = {}
    for parse_file in args.llm_file:
        llm_df = pd.read_csv(parse_file, dtype=str).fillna("")
        columns |= dict.fromkeys(llm_df.columns)
        image_paths &= set(llm_df["source"])

        llm_list = llm_df.to_dict("records")
        parsed_data[parse_file.stem] = {r["source"]: r for r in llm_list}

    # Finish building the row index
    image_paths = sorted(image_paths)
    image_paths = image_paths[: args.limit]

    # Get common rows in the original order
    columns = [k for k in columns if k not in FIRST_COLUMNS]

    # Load scoring classes
    field_classes = prompt_util.Prompt.load(args.prompt).field_classes()

    # Build rows for each group
    row_groups = []
    for i, image_path in enumerate(image_paths, 1):
        gold = gold_by_image[image_path]

        group = RowGroup(
            first_columns={
                "text": ocr_by_image[image_path]["text"],
                "source": gold["source"],
                "row_group": str(i),
            },
            gold_row={
                "row_type": "GOLD",
                **{f: gold.get(f, "") for f in columns},
            },
        )

        # Build parse rows and score rows
        for parse_file in args.parse_file:
            stem = parse_file.stem
            # Build an LLM row
            group.parse_rows.append(
                {"row_type": stem, **{c: parsed_data[stem].get(c, "") for c in columns}}
            )
            # Build a score row
            score_row = {"row_type": f"score {stem}"}
            for col in columns:
                field_class = field_classes.get(col, BaseField)
                score = field_class.score(
                    str(gold.get(col, "")),
                    str(parsed_data[stem].get(col, "")),
                    parsed_data[stem],
                )
                score_row[col] = f"{score:0.2f}"
            group.score_rows.append(score_row)

        row_groups.append(group)

    rows = []
    for group in row_groups:
        rows += group.flatten()

    df = pd.DataFrame(rows)
    df.to_csv(args.output_csv, index=False)

    log.finished()


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
            Compare the outputs of language model extracts against a gold standard.
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
        "--gold-file",
        type=Path,
        required=True,
        metavar="path",
        help="""The gold standard to compare against.""",
    )
    io_group.add_argument(
        "--parse-file",
        type=Path,
        required=True,
        action="append",
        metavar="path",
        help="""The cleaned LLM results file. You may compare several files at once.""",
    )
    io_group.add_argument(
        "--output-csv",
        type=Path,
        required=True,
        metavar="path",
        help="""Write the comparison results to this CSV file.""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt",
        type=Path,
        required=True,
        metavar="path",
        help="""A markdown file with a prompt and list of fields to parse.
            It is used to get the scoring functions.""",
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
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    score_against_gold(ARGS)
