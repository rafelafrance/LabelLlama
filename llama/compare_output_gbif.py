#!/usr/bin/env python3
"""
Compare LLM outputs against corresponding GBIF data.

Using a golden dataset would be ideal but sometimes it doesn't exist, so I use GBIF
data as an ersatz golden dataset. On the plus side, I can reverse the sense of the
compare and see how well the GBIF data actually is.

Output format: more or less
    Index: <row_group>.<column>.<llm_index>

| Text | Source  | Row group | Type    |  Column 1   |  Column 2   | ... |  Column n   |
|------|---------|-----------|---------|-------------|-------------| ... |-------------|
|      |         |           | gbif    | gbif  1.1   | gbif  1.2   | ... | gbif  1.n   |
|      |         |           | llm 1   | value 1.1.1 | value 1.2.1 | ... | value 1.n.1 |
| text | /path/1 |     1     | llm 2   | value 1.1.2 | value 1.2.2 | ... | value 1.n.2 |
|      |         |           | score 1 | score 1.1.1 | score 1.2.1 | ... | score 1.n.1 |
|      |         |           | score 2 | score 1.1.2 | score 1.2.2 | ... | score 1.n.2 |
|------|---------|-----------|---------|-------------|-------------| ... |-------------|
|      |         |           | gbif    | gbif  2.1   | gbif  2.2   | ... | gbif  2.n   |
|      |         |           | llm 1   | value 2.1.1 | value 2.2.1 | ... | value 2.n.1 |
| text | /path/2 |     2     | llm 2   | value 2.2.1 | value 2.2.2 | ... | value 2.n.2 |
|      |         |           | score 1 | score 2.1.1 | score 2.2.1 | ... | score 2.n.1 |
|      |         |           | score 2 | score 2.2.1 | score 2.2.2 | ... | score 2.n.2 |
"""

import argparse
import logging
import textwrap
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any

import pandas as pd
from rapidfuzz import fuzz
from tqdm import tqdm

from llama.pylib import io_util, log

FIRST_COLUMNS = ["text", "image_path", "row_group", "row_type", "source"]
GBIF_SEARCH_MD = Path(__file__).resolve().parent / "templates" / "gbif_search.md"


# ----------------------------------------------------------------------------------
SEARCH_SUCCESS_THRESHOLD = 0.5


class ScoreCat(Enum):
    aligned_both_full = auto()
    aligned_both_empty = auto()
    aligned_gbif_empty = auto()
    aligned_parse_empty = auto()
    not_aligned_parse_empty = auto()
    search_fail = auto()
    search_success = auto()


@dataclass
class Tally:
    aligned_both_full_count: int = 0
    aligned_both_full_average: float = 0.0
    aligned_both_empty_count: int = 0
    aligned_gbif_empty_count: int = 0
    aligned_parse_empty_count: int = 0
    not_aligned_parse_empty_count: int = 0
    search_fail_count: int = 0
    search_success_count: int = 0
    search_success_average: float = 0.0


@dataclass
class Score:
    cat: ScoreCat
    score: float = 0.0
    method: str = ""
    gbif_field: str = ""
    gbif_data: str = ""

    def __gt__(self, other: Score) -> bool:
        return (self.score, -len(self.gbif_data)) > (other.score, -len(other.gbif_data))

    @staticmethod
    def tally(row_groups: list[RowGroup]) -> dict:
        # The tally is a 3-level dict
        tallies = defaultdict(lambda: defaultdict(Tally))

        # Accumulate the scores
        for group in row_groups:
            for score_row in group.score_rows:
                row_type = ""
                for col, score in score_row.items():
                    if col == "row_type":
                        row_type = score
                        continue
                    match score.cat:
                        case ScoreCat.aligned_both_full:
                            tallies[row_type][col].aligned_both_full_count += 1
                            tallies[row_type][
                                col
                            ].aligned_both_full_average += score.score
                        case ScoreCat.aligned_both_empty:
                            tallies[row_type][col]
                        case ScoreCat.aligned_gbif_empty:
                            tallies[row_type][col].aligned_gbif_empty_count += 1
                        case ScoreCat.aligned_parse_empty:
                            tallies[row_type][col].aligned_parse_empty_count += 1
                        case ScoreCat.not_aligned_parse_empty:
                            tallies[row_type][col].not_aligned_parse_empty_count += 1
                        case ScoreCat.search_fail:
                            tallies[row_type][col].search_fail_count += 1
                        case ScoreCat.search_success:
                            tallies[row_type][col].search_success_count += 1
                            tallies[row_type][col].search_success_average += score.score
        # Make score sums an average
        stats = defaultdict(lambda: defaultdict(dict))
        for row_type, columns in tallies.items():
            for col, tally in columns.items():
                if tally.aligned_both_full_count != 0:
                    tally.aligned_both_full_average /= tally.aligned_both_full_count
                if tally.search_success_count != 0:
                    tally.search_success_average /= tally.search_success_count
                stats[row_type][col] = {k: v or "" for k, v in asdict(tally).items()}

        return stats


# ----------------------------------------------------------------------------------
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
    gbif_row: dict[str, Any] = field(default_factory=dict)
    parse_rows: list[dict[str, str]] = field(default_factory=list)
    score_rows: list[dict[str, Any]] = field(default_factory=list)

    def format(self, output_type: str) -> RowGroup:
        self.format_gbif_row(output_type)
        self.format_score_rows(output_type)
        return self

    def format_gbif_row(self, output_type: str) -> None:
        for col, scores in self.gbif_row.items():
            if col == "row_type":
                continue
            match output_type:
                case ".html":
                    values = [
                        f"<span class='label'>{s.gbif_field}</span> {s.gbif_data}"
                        for s in scores
                    ]
                    self.gbif_row[col] = "<br/>".join(values)
                case ".ods":
                    self.gbif_row[col] = ",\n".join(
                        [f"{s.gbif_field} {s.gbif_data}" for s in scores]
                    )

    def format_score_rows(self, output_type: str) -> None:
        for score_row in self.score_rows:
            for col, score in score_row.items():
                if col == "row_type":
                    continue
                match output_type:
                    case ".html":
                        score_row[col] = (
                            f"<span class='label'>{score.gbif_field}</span> "
                            f"{score.method} {score.score:0.2f}"
                        )
                    case ".ods":
                        value = f"{score.score:0.2f}"
                        score_row[col] = f"{score.gbif_field} {score.method} {value}"


# ----------------------------------------------------------------------------------
def score_against_gbif(args: argparse.Namespace) -> None:
    """Compare LLM outputs against gbif data and write an HTML report."""
    log.started(args.log_file, args=args)

    # Read OCR data
    ocr_list = io_util.read_list_of_dicts(args.ocr_file)
    ocr_by_image = {o["source"]: o for o in ocr_list}

    # Read GBIF data
    gbif_list = io_util.read_list_of_dicts(args.gbif_file)
    gbif_by_image = {g["source"]: g for g in gbif_list}

    # Init 2 of the 3 indexes for the quasi 3D struct, see this script's doc string
    image_paths = set(gbif_by_image)
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

    # If the gbif cells do not match the llm cells then search for aligned data in gbif
    gbif_search = get_gbif_search()

    output_type = args.output_csv.suffix.lower()

    # Build report lines
    row_groups: list[RowGroup] = []
    for i, image_path in enumerate(image_paths, 1):
        row_group = RowGroup(
            first_columns={
                "text": ocr_by_image[image_path]["text"],
                "image_path": image_path,
                "href": gbif_by_image[image_path]["identifier"],
                "row_group": str(i),
            }
        )

        # Build skeleton of the GBIF row. It gets filled in during scoring.
        # It will ultimately contain a list of score results.
        gbif_input = gbif_by_image[image_path]
        gbif_row: dict[str, Any] = {"row_type": "GBIF"} | {c: [] for c in columns}
        row_group.gbif_row = gbif_row

        # Build the parse and score rows
        for parse_file in args.parse_file:
            # Build LLM row. It just holds the LLM results as is
            parse_row: dict[str, str] = {"row_type": parse_file.stem} | {
                c: parsed_data[parse_file.stem][image_path][c] for c in columns
            }
            row_group.parse_rows.append(parse_row)

            # Build score row by scoring each column. This also fills in the GBIF cell
            score_row: dict[str, str | Score] = {"row_type": f"{parse_file.stem} score"}
            for col in columns:
                actual = parse_row[col]
                score = calc_score(col, actual, gbif_input, gbif_search)
                score_row[col] = score
                if score.gbif_field:
                    gbif_row[col].append(score)
            row_group.score_rows.append(score_row)

        row_groups.append(row_group)

    logging.info("Tally scores")
    stats = Score.tally(row_groups)

    for row_group in tqdm(row_groups, desc="format"):
        row_group.format(output_type)

    write_ods(
        ods_file=args.output_csv,
        row_groups=row_groups,
        gbif_search=gbif_search,
        stats=stats,
    )

    log.finished()


# ----------------------------------------------------------------------------------
def calc_score(col: str, actual: str, gbif_input: dict, gbif_search: dict) -> Score:
    expect = gbif_input.get(col)

    # If the GBIF column has a value then we score against that
    if expect is not None:
        expect = expect.strip()
        if not expect and not actual:
            return Score(cat=ScoreCat.aligned_both_empty)
        if not expect:
            return Score(cat=ScoreCat.aligned_gbif_empty)
        if not actual:
            return Score(cat=ScoreCat.aligned_parse_empty)
        score = fuzz.partial_ratio(expect, actual) / 100.0
        return Score(
            cat=ScoreCat.aligned_both_full,
            score=score,
            method="FPR",
            gbif_field=col,
            gbif_data=expect,
        )

    # If there is not value to score against then we can't search for a value
    if not actual:
        return Score(cat=ScoreCat.not_aligned_parse_empty, method="")

    # Try searching for a matching value in gbif_search columns and pick the best one
    max_score = Score(cat=ScoreCat.search_fail)

    for search_field in gbif_search.get(col, []):
        expect = gbif_input.get(search_field, "")
        if not expect:
            continue

        score = fuzz.partial_ratio(expect, actual) / 100.0
        current = Score(
            cat=ScoreCat.search_success,
            score=score,
            method="FPR",
            gbif_field=search_field,
            gbif_data=expect,
        )
        if score >= SEARCH_SUCCESS_THRESHOLD:
            max_score = max(current, max_score)

    return max_score


# ----------------------------------------------------------------------------------
def write_ods(
    ods_file: Path,
    row_groups: list[RowGroup],
    gbif_search: dict,
    stats: dict,
) -> None:
    logging.info("Building stats tab")
    stats_rows = []
    for stem, fields in stats.items():
        for col, data in fields.items():
            stats_rows.append({"file": stem, "column": col, **data})
    stats_df = pd.DataFrame(stats_rows)

    rows = []
    for row_group in tqdm(row_groups, desc="build detail"):
        rows.append(row_group.first_columns | row_group.gbif_row)
        rows += [row_group.first_columns | row for row in row_group.parse_rows]
        rows += [row_group.first_columns | row for row in row_group.score_rows]
    group_df = pd.DataFrame(rows)

    logging.info("Building GBIF search tab")
    gbif_rows = [
        {"field": k, "search fields": ", ".join(v)} for k, v in gbif_search.items()
    ]
    gbif_df = pd.DataFrame(gbif_rows)

    logging.info(f"Write {ods_file.name}")
    with pd.ExcelWriter(ods_file, engine="odf") as writer:
        stats_df.to_excel(writer, sheet_name="statistics", index=False)
        group_df.to_excel(writer, sheet_name="detail", index=False)
        gbif_df.to_excel(writer, sheet_name="gbif_search_fields", index=False)


# ----------------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------------
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
        "--parse-file",
        type=Path,
        required=True,
        action="append",
        metavar="path",
        help="""The cleaned LLM parse file. You may compare several files at once.""",
    )
    io_group.add_argument(
        "--output-csv",
        type=Path,
        required=True,
        metavar="path",
        help="""Write the comparison results to this CSV file.""",
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
    score_against_gbif(ARGS)
