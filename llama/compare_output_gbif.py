#!/usr/bin/env python3
"""
Compare LLM outputs against corresponding GBIF data.

Using a golden dataset would be ideal but sometimes it doesn't exist, so I use GBIF
data as an ersatz golden dataset. On the plus side, I can reverse the sense of the
compare and see how well the GBIF actually is.
"""

import argparse
import textwrap
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import jinja2
from rapidfuzz import fuzz
from tqdm import tqdm

from llama.pylib import io_util, log

FIRST_COLUMNS = ["text", "source", "row", "type"]
GBIF_SEARCH_MD = Path(__file__).resolve().parent / "templates" / "gbif_search.md"


@dataclass
class Accumulator:
    """Collect various statistics for the report."""

    gbif_has_value: dict = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list))
    )
    field_empty: dict = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list))
    )
    search_fail: dict = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list))
    )
    search_success: dict = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list))
    )

    def format(self, llm_files: list[Path], columns: list[str]) -> dict:
        """Convert the collected data into a usable form for the report."""
        stats = defaultdict(lambda: defaultdict(dict))
        for llm_file in llm_files:
            stem = llm_file.stem
            for col in columns:
                count, avg = "", ""
                if self.gbif_has_value.get(stem) and self.gbif_has_value[stem].get(col):
                    values = self.gbif_has_value[stem][col]
                    count = str(len(values))
                    avg = f"{sum(values) / len(values):0.2f}"
                stats[stem][col]["gbif_has_value_count"] = count
                stats[stem][col]["gbif_has_value_average"] = avg

                count = ""
                if self.field_empty.get(stem) and self.field_empty[stem].get(col):
                    count = str(len(self.field_empty[stem][col]))
                stats[stem][col]["field_empty_count"] = count

                count = ""
                if self.search_fail.get(stem) and self.search_fail[stem].get(col):
                    count = str(len(self.search_fail[stem][col]))
                stats[stem][col]["search_fail_count"] = count

                count, avg = "", ""
                if self.search_success.get(stem) and self.search_success[stem].get(col):
                    values = self.search_success[stem][col]
                    count = str(len(values))
                    avg = f"{sum(values) / len(values):0.2f}"
                stats[stem][col]["search_success_count"] = count
                stats[stem][col]["search_success_average"] = avg

        return stats


@dataclass
class RowGroup:
    """A group of rows that get displayed together."""

    gbif_row: dict = field(default_factory=dict)
    llm_rows: list[dict] = field(default_factory=list)
    score_rows: list[dict] = field(default_factory=list)


def score_against_gbif(args: argparse.Namespace) -> None:
    """Compare LLM outputs against gbif data and write an HTML report."""
    log.started(args.log_file, args=args)

    # Read OCR data
    ocr_df = io_util.read_to_df(args.ocr_file)
    ocr_dict = {o["source"]: o for o in ocr_df.to_dict("records")}

    # Read GBIF data
    gbif_df = io_util.read_to_df(args.gbif_file)
    gbif_dict = {g["source"]: g for g in gbif_df.to_dict("records")}

    # Init row and column indexes
    row_index = set(gbif_dict)
    columns = {}

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

    # Setup
    aligned = set(gbif_df.columns) & set(columns)
    gbif_search = get_gbif_search()

    accumulator = Accumulator()

    # Build output row groups
    row_groups = []
    for i, source in tqdm(enumerate(row_index, 1), total=len(row_index)):
        gbif = gbif_dict[source]

        # Build gbif row
        group = RowGroup(
            gbif_row={
                "text": ocr_dict.get(source, {}).get("text", ""),
                "source": gbif["source"],
                "href": gbif["identifier"],
                "row": i,
                "type": "GBIF",
                **{
                    c: f"<span class='label'>{c}</span>{gbif[c]}"
                    if c in aligned
                    else ""
                    for c in columns
                },
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
                    field=col,
                    llm_row=llm_dict[source],
                    gbif_row=gbif,
                    gbif_search=gbif_search,
                    accumulator=accumulator,
                    stem=stem,
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

        row_groups.append(group)

    write_template(
        html_file=args.html_file,
        columns=columns,
        row_groups=row_groups,
        row_span=len(llm_dicts) * 2 + 1,  # gbif + llm + score per file
        gbif_search=gbif_search,
        accumulator=accumulator,
        llm_files=args.llm_file,
        notes=args.notes,
    )

    log.finished()


def calc_score(
    field: str,
    llm_row: dict,
    gbif_row: dict,
    gbif_search: dict,
    accumulator: Accumulator,
    stem: str,
) -> tuple[str, str | None]:
    actual = llm_row[field]

    if gbif_row.get(field):
        score = fuzz.partial_ratio(gbif_row[field], actual) / 100.0
        accumulator.gbif_has_value[stem][field].append(score)
        return f"FPR: {score:0.2f}", None

    if not actual:
        accumulator.field_empty[stem][field].append(1)
        return "NONE: 1.0", None

    max_score = (-1.0, 0)
    max_field, max_expect = "", ""

    for search_field in gbif_search.get(field, []):
        expect = gbif_row.get(search_field, "")
        if not expect:
            continue
        score = fuzz.partial_ratio(expect, actual) / 100.0
        if (score, -len(expect)) > max_score and score > 0.0:
            max_field = search_field
            max_score = (score, -len(expect))
            max_expect = expect

    if max_field:
        accumulator.search_success[stem][field].append(max_score[0])
    else:
        accumulator.search_fail[stem][field].append(1)

    cell = f"<span class='label'>{max_field}</span>{max_expect}" if max_field else None
    return f"<span class='label'>{max_field}</span>FPR: {max_score[0]:0.2f}", cell


def get_gbif_search() -> dict[str, list[str]]:
    with GBIF_SEARCH_MD.open() as inf:
        lines = [ln for line in inf.readlines() if (ln := line.strip())]
    key = ""
    search = defaultdict(list)
    for ln in lines:
        if ln.startswith("#####"):
            key = ln.rsplit(maxsplit=1)[-1]
        elif ln.startswith("-"):
            field = ln.rsplit(maxsplit=1)[-1]
            search[key].append(field)
    return search


def write_template(
    html_file: Path,
    columns: list[str],
    row_groups: list[RowGroup],
    row_span: int,
    gbif_search: dict,
    accumulator: Accumulator,
    llm_files: list[Path],
    notes: str,
) -> None:

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(Path(__file__).resolve().parent / "templates"),
        autoescape=True,
    )

    template = env.get_template("compare_output_gbif.html").render(
        now=datetime.now().strftime("%Y-%m-%d %H:%M"),
        columns=columns,
        headers=FIRST_COLUMNS + columns,
        groups=row_groups,
        row_span=row_span,
        gbif_search=gbif_search,
        stats=accumulator.format(llm_files, columns),
        notes=notes,
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
            buried in the "locality" field in GBIF but it may be broken into
            utm (the verbatim part), utmNorthing, utmEasting, and utmZone in the LLM
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
        "--ocr-file",
        type=Path,
        required=True,
        metavar="path",
        help="""This file contains the original OCRed text.""",
    )
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
    score_against_gbif(ARGS)
