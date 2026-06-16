#!/usr/bin/env python3

import argparse
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import jinja2

from llama.fields.base_field import BaseField
from llama.pylib import io_util, log, prompt_util

KEEP = [
    "institutionID",
    "collectionID",
    "datasetID",
    "institutionCode",
    "collectionCode",
    "datasetName",
    "dynamicProperties",
    "occurrenceID",
    "catalogNumber",
    "recordNumber",
    "recordedBy",
    "recordedByID",
    "sex",
    "lifeStage",
    "reproductiveCondition",
    "associatedTaxa",
    "occurrenceRemarks",
    "verbatimLabel",
    "eventType",
    "fieldNumber",
    "eventDate",
    "verbatimEventDate",
    "habitat",
    "fieldNotes",
    "eventRemarks",
    "waterBody",
    "islandGroup",
    "island",
    "countryCode",
    "stateProvince",
    "county",
    "municipality",
    "locality",
    "verbatimLocality",
    "verbatimElevation",
    "verticalDatum",
    "verbatimDepth",
    "locationRemarks",
    "decimalLatitude",
    "decimalLongitude",
    "coordinateUncertaintyInMeters",
    "coordinatePrecision",
    "identifiedBy",
    "identifiedByID",
    "dateIdentified",
    "scientificName",
    "family",
    "genus",
    "subgenus",
    "specificEpithet",
    "infraspecificEpithet",
    "cultivarEpithet",
    "elevation",
    "elevationAccuracy",
    "species",
]


@dataclass
class Group:
    source: str
    gold: dict
    clean: dict[str, dict] = field(default_factory=dict)
    gold_row: dict = field(default_factory=dict)
    clean_rows: list[dict] = field(default_factory=list)
    score_rows: list[dict] = field(default_factory=list)


def score_extracts(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    gold_df = io_util.read_to_df(args.gold_file).set_index("source", drop=False)
    gold_columns = dict.fromkeys(gold_df.columns)
    groups = {
        g["source"]: Group(source=g["source"], gold=g)
        for g in gold_df.fillna("").to_dict("records")
    }

    clean_dfs = []
    clean_columns = {}
    clean_index = set()
    clean_data = {}
    for clean_file in args.clean_file:
        clean_df = io_util.read_to_df(clean_file).set_index("source", drop=False)
        clean_dfs.append(clean_df)
        clean_columns |= dict.fromkeys(clean_df)
        clean_index |= set(clean_df.index)
        clean_data = clean_df.fillna("").to_dict("records")

        for clean_row in clean_data:
            source = groups[clean_row["source"]]
            source.clean[clean_file.stem] = clean_row

    skips = ["text", "source", "gbif", "row", "type"]
    fields = [c for c in clean_columns if c in gold_columns and c not in skips]
    columns = skips + fields

    prompt = prompt_util.Prompt.load(args.prompt)
    field_classes = prompt.field_classes()

    first = args.clean_file[0].stem
    for i, group in enumerate(groups.values(), 1):
        gold = group.gold

        # Gold row
        gold_row = {
            "source": gold["source"],
            "gbif": get_gbif_html(gold, fields),
            "text": group.clean[first]["text"],
            "row": str(i),
            "type": "gold",
        }
        for field_ in fields:
            gold_row[field_] = gold.get(field_, "")
        group.gold_row = gold_row

        # LLM rows
        for clean_file in args.clean_file:
            key = clean_file.stem
            clean = group.clean[key]
            clean_row = {"type": key}
            for field_ in fields:
                clean_row[field_] = clean.get(field_, "")
            group.clean_rows.append(clean_row)

        # Score rows
        for clean_file in args.clean_file:
            key = clean_file.stem
            clean = group.clean[key]
            score_row = {"type": key}
            for field_ in fields:
                expect = str(gold.get(field_, ""))
                actual = str(clean.get(field_, ""))
                field_action = field_classes.get(field_, BaseField)
                score = field_action.score(expect, actual, clean)
                score_row[field_] = f"{score:0.2f}"
            group.clean_rows.append(score_row)

    row_span = len(args.clean_file) * 2 + 1
    write_template(args.html_file, columns, fields, list(groups.values()), row_span)

    log.finished()


def get_gbif_html(row: dict, fields: list) -> str:
    parts = []
    parts.append("<div class='gbif'>")
    first = True
    for key, value in row.items():
        if key in fields:
            continue
        if not value or key not in KEEP:
            continue
        if first:
            first = False
        else:
            parts.append("<br/>")
        parts.append(f'<span class="gbif-key">{key}</span>')
        parts.append(f'<span class="gbif-value">{value}</span>')
    parts.append("</div>")
    return "".join(parts)


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
            """Compare the outputs of two language model (LM) runs. One run is typically
            a gold standard, but this is not a requirement, and you may want to compare
            LM outputs for various reasons.""",
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
            It is used to get the correct version of the scoring modules.""",
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
        help="""Notes for logging. They only appear in the log file.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    score_extracts(ARGS)
