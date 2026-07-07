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
from datetime import datetime
from pathlib import Path

import jinja2
from tqdm import tqdm

from llama.fields.base_field import BaseField
from llama.pylib import io_util, log, prompt_util

FIRST_COLUMNS = ["text", "source", "row_group"]  # , "row_type"]


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
    llm_rows: list[dict] = field(default_factory=list)
    score_rows: list[dict] = field(default_factory=list)


def score_against_gold(args: argparse.Namespace) -> None:
    """
    Compare LLM outputs against a gold standard and write an HTML report.

    I'm building table with groups of rows. Each group of rows is indexed by
    the image source (its path).
    """
    log.started(args.log_file, args=args)

    # Read OCR data
    ocr_df = io_util.read_to_df(args.ocr_file)
    ocr_dict = {o["source"]: o for o in ocr_df.to_dict("records")}

    # Read Gold data
    gold_df = io_util.read_to_df(args.gold_file)
    gold_dict = {g["source"]: g for g in gold_df.to_dict("records")}

    # Init row and column indexes
    row_index = set(gold_dict)
    columns = dict.fromkeys(gold_dict)

    # Read LLM data
    llm_dicts = {}
    for llm_file in args.llm_file:
        llm_df = io_util.read_to_df(llm_file)
        llm_dict = {r["source"]: r for r in llm_df.to_dict("records")}
        llm_dicts[llm_file.stem] = llm_dict
        row_index &= set(llm_dict)
        columns |= dict.fromkeys(llm_df.columns)

    # Init the row index
    row_index = sorted(row_index)
    row_index = row_index[: args.limit] if args.limit else row_index

    # Get common rows in the original order
    columns = [k for k in columns if k not in FIRST_COLUMNS]

    # Load scoring classes
    field_classes = prompt_util.Prompt.load(args.prompt).field_classes()

    # Build comparison rows for each group
    row_groups = []
    for i, source in tqdm(enumerate(row_index, 1), total=len(row_index)):
        gold = gold_dict[source]

        # Build the golden row
        group = RowGroup(
            gold_row={
                "text": ocr_dict.get(source, {}).get("text", ""),
                "source": gold["source"],
                "row_group": i,
                "row_type": "gold",
                **{f: gold.get(f, "") for f in columns},
            }
        )

        # Build LLM rows and score rows
        for stem, llm_dict in llm_dicts.items():
            # Build an LLM row
            group.llm_rows.append(
                {"type": stem, **{c: llm_dict.get(c, "") for c in columns}}
            )
            # Build a score row
            score_row = {"type": f"score: {stem}"}
            for col in columns:
                field_class = field_classes.get(col, BaseField)
                score = field_class.score(
                    str(gold.get(col, "")),
                    str(llm_dict.get(col, "")),
                    llm_dict,
                )
                score_row[col] = f"{score:0.2f}"
            group.score_rows.append(score_row)

        row_groups.append(group)

    # Write report
    write_template(
        html_file=args.html_file,
        columns=FIRST_COLUMNS + columns,
        fields=columns,
        row_groups=row_groups,
        row_span=len(args.llm_file) * 2 + 1,  # gold + llm + score per file
        notes=args.notes,
    )

    log.finished()


def write_template(
    html_file: Path,
    columns: list[str],
    fields: list[str],
    row_groups: list[RowGroup],
    row_span: int,
    notes: str,
) -> None:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(Path(__file__).resolve().parent / "templates"),
        autoescape=True,
    )

    template = env.get_template("compare_output_gold.html").render(
        now=datetime.now().strftime("%Y-%m-%d %H:%M"),
        columns=columns,
        fields=fields,
        groups=row_groups,
        row_span=row_span,
        notes=notes,
    )

    with html_file.open("w") as fout:
        fout.write(template)


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
        "--llm-file",
        type=Path,
        required=True,
        action="append",
        metavar="path",
        help="""The cleaned LLM results file. You may compare several files at once.""",
    )
    io_group.add_argument(
        "--html-file",
        type=Path,
        required=True,
        help="""Write the comparison results to this HTML file.""",
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
