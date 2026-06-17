#!/usr/bin/env python3

import argparse
import textwrap
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from pprint import pp

import jinja2
from rapidfuzz import fuzz
from tqdm import tqdm

from llama.fields.base_field import BaseField
from llama.pylib import io_util, log, prompt_util

FIRST_COLUMNS = ["text", "source", "row", "type"]


@dataclass
class Group:
    gbif_row: dict = field(default_factory=dict)
    llm_rows: list[dict] = field(default_factory=list)
    score_rows: list[dict] = field(default_factory=list)


def score_extracts(args: argparse.Namespace) -> None:
    """Compare LLM outputs against gbif data and write an HTML report."""
    log.started(args.log_file, args=args)

    # Load data
    gbif_df = io_util.read_to_df(args.gbif_file)
    gbif_dict = {g["source"]: g for g in gbif_df.to_dict("records")}

    sources = set(gbif_dict)
    columns = {}

    llm_dicts = {}
    first = None
    for llm_file in args.llm_file:
        llm_df = io_util.read_to_df(llm_file)
        llm_dict = {r["source"]: r for r in llm_df.to_dict("records")}
        key = llm_file.stem
        llm_dicts[key] = llm_dict
        first = key or first
        sources &= set(llm_dict)
        columns |= dict.fromkeys(llm_df.columns)

    sources = sorted(sources)
    sources = sources[: args.limit]

    columns = [k for k in columns if k not in FIRST_COLUMNS]

    classes = prompt_util.Prompt.load(args.prompt).field_classes()
    accum = defaultdict(float)
    groups = []

    for i, source in tqdm(enumerate(sources, 1), total=len(sources)):
        gbif = gbif_dict[source]

        # Build gbif row
        group = Group(
            gbif_row={
                "text": llm_dicts[first][source]["text"],
                "source": gbif["source"],
                "row": i,
                "type": "GBIF",
                **{c: gbif.get(c, "") for c in columns},
            }
        )

        # Build LLM data rows
        for stem, llm_dict in llm_dicts.items():
            group.llm_rows.append(
                {
                    "type": stem,
                    **{c: llm_dict[source].get(c, "") for c in columns},
                }
            )

        # Build score rows
        for stem, llm_dict in llm_dicts.items():
            row = {"type": f"score: {stem}"}
            for col in columns:
                score, expect = calc_score(
                    col, llm_dict[source].get(col, ""), gbif, classes, accum
                )
                row[col] = score
                if expect is not None:
                    prev = group.gbif_row[col]
                    if prev.find(expect) > -1:
                        continue
                    if prev:
                        group.gbif_row[col] += "<br/>"
                    group.gbif_row[col] += expect
            group.score_rows.append(row)

        groups.append(group)

    write_template(args.html_file, columns, groups, len(llm_dicts) * 2 + 1)

    log.finished()


def calc_score(
    field: str, actual: str, gbif: dict, field_classes: dict[str, type], accum: dict
) -> tuple[str, str | None]:
    if gbif.get(field):
        field_class = field_classes.get(field, BaseField)
        score = field_class.score(gbif[field], actual, gbif)
        accum[field] += score
        return f"{field_class.scoring_method}: {score:0.2f}", None

    if not actual and not gbif.get(field):
        accum[field] += 1.0
        return "1.0", None

    max_score = (0.0, 0.0)
    max_field, max_expect = "", ""
    for column, expect in {k: v for k, v in gbif.items() if v}.items():
        ratio = fuzz.partial_ratio(expect, actual) / 100
        score = (ratio, len(actual) / len(expect))
        if score > max_score:
            max_field = column
            max_score = score
            max_expect = expect

    accum[field] += max_score[0]

    cell = f"<span class='label'>{max_field}</span>{max_expect}" if max_field else None
    return f"<span class='label'>{max_field}</span>FPR: {max_score[0]:0.2f}", cell


def write_template(
    html_file: Path, columns: list[str], groups: list[dict], row_span: int
) -> None:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(Path() / "llama" / "templates"),
        autoescape=True,
    )

    template = env.get_template("compare_output_gbif.html").render(
        now=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M"),
        columns=columns,
        headers=FIRST_COLUMNS + columns,
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
            Compare the outputs of language model extracts against GBIF data.

            Sometimes you don't have an actual gold standard but you do have actual
            GBIF data associated with the label images. Here I try to leverage the
            GBIF data as a quasi-gold standard and compare the extracted data against
            that.

            The problem with using GBIF data is that many columns from GBIF do not
            align with the columns in the LLM output data. For instance a UTM may be
            burried in the "locality" field in GBIF but it may be broken into
            utm (the verbatim part), utmNorthing, utmEasing, and utmZone in the LLM
            output. To handle this I will scan GBIF data for fields that match the
            little LLM fields and score those. So "UTM 17 495432E, 2926666N" in GBIF's
            locality field will match against all utm = "UTM 17 495432E, 2926666N",
            utmNorthing = "2926666", utmEasting = "495432", and utmZone = "17". All
            with a perfect 1.0 score.
            """,
        ),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--gbif-file",
        type=Path,
        required=True,
        metavar="path",
        help="""The GBIF data to compare against.""",
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
    debugging_group = arg_parser.add_argument_group("debugging options")
    debugging_group.add_argument(
        "--limit",
        type=int,
        metavar="int",
        help="""Only score this many records.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    score_extracts(ARGS)
