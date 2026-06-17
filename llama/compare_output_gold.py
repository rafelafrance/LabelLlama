#!/usr/bin/env python3

import argparse
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import jinja2

from llama.fields.base_field import BaseField
from llama.pylib import io_util, log, prompt_util

SKIP_COLUMNS = ["text", "source", "row", "type"]
_SKIP_SET = frozenset(SKIP_COLUMNS)


@dataclass
class Group:
    source: str
    gold: dict
    clean: dict[str, dict] = field(default_factory=dict)
    gold_row: dict = field(default_factory=dict)
    clean_rows: list[dict] = field(default_factory=list)
    score_rows: list[dict] = field(default_factory=list)


def score_extracts(args: argparse.Namespace) -> None:
    """Compare LLM outputs against a gold standard and write an HTML report."""
    log.started(args.log_file, args=args)

    # Load data
    groups, gold_columns = _load_gold_groups(args.gold_file)
    column_sets = _load_clean_data(groups, args.clean_file)
    fields = _common_fields(column_sets, gold_columns)
    clean_keys = [f.stem for f in args.clean_file]

    # Load scoring classes
    field_classes = prompt_util.Prompt.load(args.prompt).field_classes()

    # Build comparison rows for each group
    for i, group in enumerate(groups.values(), 1):
        group.gold_row = _build_gold_row(
            group.gold,
            group.clean[clean_keys[0]]["text"],
            fields,
            i,
        )
        for key in clean_keys:
            group.clean_rows.append(_build_clean_row(group.clean[key], key, fields))
            group.score_rows.append(
                _build_score_row(
                    group.gold, group.clean[key], key, fields, field_classes
                )
            )

    # Write report
    row_span = len(args.clean_file) * 2 + 1  # gold + clean + score per file
    write_template(
        args.html_file,
        list(SKIP_COLUMNS) + fields,
        fields,
        list(groups.values()),
        row_span,
    )

    log.finished()


def _load_gold_groups(gold_file: Path) -> tuple[dict[str, Group], set]:
    """
    Load gold-standard data into a dict keyed by source.

    Returns (groups, gold_column_set).
    """
    gold_df = io_util.read_to_df(gold_file).set_index("source", drop=False)
    gold_columns = set(gold_df.columns)
    return {
        g["source"]: Group(source=g["source"], gold=g)
        for g in gold_df.fillna("").to_dict("records")
    }, gold_columns


def _load_clean_data(
    groups: dict[str, Group],
    clean_files: list[Path],
) -> dict[str, set]:
    """Populate each group's clean dict and return per-file column sets."""
    column_sets: dict[str, set] = {}
    for clean_file in clean_files:
        clean_df = io_util.read_to_df(clean_file).set_index("source", drop=False)
        column_sets[clean_file.stem] = set(clean_df.columns)
        for clean_row in clean_df.fillna("").to_dict("records"):
            groups[clean_row["source"]].clean[clean_file.stem] = clean_row
    return column_sets


def _common_fields(
    column_sets: dict[str, set],
    gold_columns: set,
) -> list[str]:
    """Return columns shared across all clean files and gold, excluding metadata."""
    shared = column_sets.values().__iter__().__next__()
    for col_set in column_sets.values():
        shared &= col_set
    return sorted(shared & gold_columns - _SKIP_SET)


def _build_gold_row(
    gold: dict,
    clean_text: str,
    fields: list[str],
    row_num: int,
) -> dict:
    """Build the gold-standard comparison row."""
    return {
        "source": gold["source"],
        "text": clean_text,
        "row": str(row_num),
        "type": "gold",
        **{f: gold.get(f, "") for f in fields},
    }


def _build_clean_row(clean: dict, clean_key: str, fields: list[str]) -> dict:
    """Build a single LLM output row."""
    return {"type": clean_key, **{f: clean.get(f, "") for f in fields}}


def _build_score_row(
    gold: dict,
    clean: dict,
    clean_key: str,
    fields: list[str],
    field_classes: dict[str, type],
) -> dict:
    """Build a single score row comparing gold against one LLM output."""
    score_row = {"type": clean_key}
    for f in fields:
        field_class = field_classes.get(f, BaseField)
        score = field_class.score(
            str(gold.get(f, "")),
            str(clean.get(f, "")),
            clean,
        )
        score_row[f] = f"{score:0.2f}"
    return score_row


def write_template(
    html_file: Path,
    columns: list[str],
    fields: list[str],
    groups: list[Group],
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
            Compare the outputs of language model extracts against a gold standard.
            """,
        ),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--gold-file",
        type=Path,
        required=True,
        metavar="path",
        help="""The gold standard to compare against.""",
    )
    io_group.add_argument(
        "--clean-file",
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
    score_extracts(ARGS)
