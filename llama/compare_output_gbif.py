#!/usr/bin/env python3
"""
Compare LLM outputs against corresponding GBIF data.

Using a golden dataset would be ideal but sometimes it doesn't exist, so I use GBIF
data as an ersatz golden dataset. On the plus side, I can reverse the sense of the
compare and see how well the GBIF actually is.
"""

import argparse
import re
import textwrap
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import jinja2
import pandas as pd
from pandas.core.window.ewm import dtype_to_unit
from rapidfuzz import fuzz
from tqdm import tqdm

from llama.pylib import io_util, log

FIRST_COLUMNS = ["text", "source", "row_group", "type"]
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

    def to_dict(self, llm_files: list[Path], columns: list[str]) -> dict:
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


@dataclass
class LlmCell:
    text: str = ""  # The cell's text
    score: float = 0.0  # The score the cell got
    score_method: str = ""  # How the cell was scored
    gbif_cell: str = ""  # What cell provided the best match


@dataclass
class GbifCell:
    original: str = ""
    # What cells matched llm cells best. We search for best matches in the GBIF row
    matches: dict[str, str] = field(default_factory=dict)


@dataclass
class CellGroup:
    header: str = ""  # Column header for the cell group
    gbif_cells: list[GbifCell] = field(default_factory=list)
    llm_cells: list[LlmCell] = field(default_factory=list)


@dataclass
class RowGroup2:
    row_num: int = 0  # Index for the group. A simple enumerate starting at 1
    text: str = ""  # What is the OCRed text
    source: str = ""  # The name of the image file or source CSV file
    href: str = ""  # A link back to the original gbif record
    cells: list[CellGroup] = field(default_factory=list)  # Column -> CellGroup


def score_against_gbif_new(args: argparse.Namespace) -> None:
    """Compare LLM outputs against gbif data and write an HTML report."""
    log.started(args.log_file, args=args)

    suffix = args.output_file.suffix.lower()

    # Read OCR data
    ocr_list = io_util.read_list_of_dicts(args.ocr_file)
    ocr_dict = {o["source"]: o for o in ocr_list}

    # Read GBIF data
    gbif_list = io_util.read_list_of_dicts(args.gbif_file)
    gbif_dict = {g["source"]: g for g in gbif_list}

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

    # Get common columns in the original order
    columns = [k for k in columns if k not in FIRST_COLUMNS]

    # Build RowGroups
    row_groups = []
    for i, source in tqdm(enumerate(row_index, 1), total=len(row_index)):
        gbif = gbif_dict[source]

        row_group = RowGroup2(
            row_num=i,
            text=ocr_dict.get(source, {}).get("text", ""),
            source=gbif["source"],
            href=gbif["identifier"],
        )

        for col in columns:
            cell_group = CellGroup(
                header=col,
                gbif_cells=[GbifCell(original=gbif_dict[source][c]) for c in columns],
            )
            for llm_dict in llm_dicts.values():
                cell_group.llm_cells += [llm_dict[c] for c in columns]


def score_against_gbif(args: argparse.Namespace) -> None:
    """Compare LLM outputs against gbif data and write an HTML report."""
    log.started(args.log_file, args=args)

    suffix = args.output_file.suffix.lower()

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

        # These are only displayed once with rowspan for .html, but duplicated for .ods
        first_cols = {
            "text": ocr_dict.get(source, {}).get("text", ""),
            "source": gbif["source"],
            "href": gbif["identifier"],
            "row_group": i,
        }

        # Build gbif row
        group = RowGroup(
            gbif_row={
                **first_cols,
                "type": "GBIF",
                **{
                    c: format_output(
                        suffix, f"<span class='label'>{c}</span> {gbif[c]}"
                    )
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
                    **first_cols,
                    "type": stem,
                    **{c: llm_dict[source].get(c, "") for c in columns},
                }
            )

        # Build score rows
        for stem, llm_dict in llm_dicts.items():
            row = {**first_cols, "type": f"score: {stem}"}
            for col in columns:
                score, expect = calc_score(
                    field=col,
                    llm_row=llm_dict[source],
                    gbif_row=gbif,
                    gbif_search=gbif_search,
                    accumulator=accumulator,
                    stem=stem,
                    suffix=suffix,
                )
                row[col] = score
                if expect is not None:
                    prev = group.gbif_row[col]
                    if prev.find(expect) > -1:
                        continue
                    if prev:
                        group.gbif_row[col] += format_output(suffix, "<br/>")
                    group.gbif_row[col] += expect
            group.score_rows.append(row)

        row_groups.append(group)

    stats = accumulator.to_dict(args.llm_file, columns)

    match suffix:
        case ".html":
            write_html(
                html_file=args.output_file,
                columns=columns,
                row_groups=row_groups,
                row_span=len(llm_dicts) * 2 + 1,  # gbif + llm + score per file
                gbif_search=gbif_search,
                stats=stats,
                notes=args.notes,
            )
        case ".ods":
            write_ods(
                output_file=args.output_file,
                row_groups=row_groups,
                gbif_search=gbif_search,
                stats=stats,
                engine="odf",
            )

    log.finished()


def format_output(suffix: str, text: str) -> str:
    """Convert HTML to plain old text depending on the output file's suffix."""
    if suffix == ".html":
        return text
    text = text.replace("<br/>", "\n")
    text = re.sub(r"<span[^>]*>", "", text)
    text = text.replace("</span>", ":")
    return text


def write_ods(
    output_file: Path,
    row_groups: list[RowGroup],
    gbif_search: dict,
    stats: dict,
    engine: str,
) -> None:
    stats_rows = []
    for stem, fields in stats.items():
        for col, data in fields.items():
            stats_rows.append({"file": stem, "column": col, **data})
    stats_df = pd.DataFrame(stats_rows)

    group_rows = []
    for group in row_groups:
        group_rows.append(group.gbif_row)
        group_rows += group.llm_rows
        group_rows += group.score_rows
    group_df = pd.DataFrame(group_rows)

    gbif_rows = [
        {"field": k, "search fields": ", ".join(v)} for k, v in gbif_search.items()
    ]
    gbif_df = pd.DataFrame(gbif_rows)

    with pd.ExcelWriter(output_file, engine=engine) as writer:
        stats_df.to_excel(writer, sheet_name="statistics", index=False)
        group_df.to_excel(writer, sheet_name="detail", index=False)
        gbif_df.to_excel(writer, sheet_name="gbif_search_fields", index=False)


def write_html(
    html_file: Path | str,
    columns: list[str],
    row_groups: list[RowGroup],
    row_span: int,
    gbif_search: dict,
    stats: dict,
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
        stats=stats,
        notes=notes,
    )

    with Path(html_file).open("w") as fout:
        fout.write(template)


def calc_score(
    field: str,
    llm_row: dict,
    gbif_row: dict,
    gbif_search: dict,
    accumulator: Accumulator,
    stem: str,
    suffix: str,
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

    gbif_cell = (
        format_output(suffix, f"<span class='label'>{max_field}</span> {max_expect}")
        if max_field
        else None
    )
    score_cell = format_output(
        suffix, f"<span class='label'>{max_field}</span> FPR: {max_score[0]:0.2f}"
    )
    return score_cell, gbif_cell


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
        "--output-file",
        type=Path,
        required=True,
        help="""Write the comparison results to this file. The file suffix
            (.html or .ods) determines the file type.""",
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
