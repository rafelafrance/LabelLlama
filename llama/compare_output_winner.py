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
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import jinja2

from llama.fields.base_field import BaseField
from llama.pylib import io_util, log, prompt_util

FIRST_COLUMNS = ["text", "source", "row_group", "row_type"]


@dataclass
class RowGroup:
    first_columns: dict[str, str] = field(default_factory=dict)
    parse_rows: list[dict[str, str]] = field(default_factory=list)
    winner_row: dict[str, Any] = field(default_factory=dict)


def compare_model_winner(args: argparse.Namespace) -> None:
    """Compare LLM outputs against each other and choose a winner."""
    log.started(args.log_file, args=args)

    # Read OCR data
    ocr_list = io_util.read_list_of_dicts(args.ocr_file)
    ocr_by_image = {o["source"]: o for o in ocr_list}

    # Init 2 of the 3 indexes for the quasi 3D struct, see this script's doc string
    image_paths = set()
    column_keys = {}

    # Get parsed data
    parsed_data = {}
    for parse_file in args.parse_file:
        llm_df = io_util.read_to_df(parse_file)
        column_keys |= dict.fromkeys(llm_df.columns)
        image_paths &= set(llm_df["source"])

        llm_list = llm_df.to_dict("records")
        parsed_data[parse_file.stem] = {r["source"]: r for r in llm_list}

    # Finish building the row index
    image_paths = sorted(image_paths)
    image_paths = image_paths[: args.limit]

    # Get common columns in the original order
    columns = [k for k in column_keys if k not in FIRST_COLUMNS]

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
            group.parse_rows.append(
                {"row_type": stem, **{c: parsed_data[stem].get(c, "") for c in columns}}
            )

    log.finished()


def write_html(
    html_file: Path,
    columns: list[str],
    fields: list[str],
    row_groups: list[RowGroup],
    row_span: int,
) -> None:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(Path() / "llama" / "templates"),
        autoescape=True,
    )

    template = env.get_template("compare_output_gold.html").render(
        now=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M"),
        columns=columns,
        fields=fields,
        groups=groups,
        row_span=row_span,
    )

    with html_file.open("w") as fout:
        fout.write(template)


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
        "--output-file",
        type=Path,
        required=True,
        help="""Write the comparison results to this file. The file suffix
            (.html or .ods) determines the file type.""",
    )
    winner_group = arg_parser.add_argument_group("Majority options")
    winner_group.add_argument(
        "--majority",
        action="store_try",
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
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    compare_model_winner(ARGS)
