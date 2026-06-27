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
import textwrap
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz

from llama.pylib import io_util, log

FIRST_COLUMNS = ["text", "source", "row_group", "row_type"]
GBIF_SEARCH_MD = Path(__file__).resolve().parent / "templates" / "gbif_search.md"


class ScoreCat(Enum):
    gbif_has_value = auto()
    both_empty = auto()
    search_fail = auto()
    search_success = auto()


@dataclass
class Score:
    cat: ScoreCat
    score: float | None = None
    method: str | None = None
    gbif_field: str | None = None
    gbif_data: str | None = None

    @staticmethod
    def is_score(row: dict) -> bool:
        return row["row_type"].endswith("score")

    @staticmethod
    def tally(rows: list[dict]) -> dict:
        return {}


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

    # Get llm data
    llm_data = defaultdict(dict)
    for llm_file in args.llm_file:
        llm_df = io_util.read_to_df(llm_file)
        column_keys |= dict.fromkeys(llm_df.columns)
        image_paths &= set(llm_df["source"])

        llm_list = llm_df.to_dict("records")
        llm_data[llm_file.stem] = {r["source"]: r for r in llm_list}

    # Finish building the row index
    image_paths = sorted(image_paths)
    image_paths = image_paths[: args.limit] if args.limit else image_paths

    # Get common columns in the original order
    columns = [k for k in column_keys if k not in FIRST_COLUMNS]

    # If the gbif cells do not match the llm cells then search for aligned data in gbif
    gbif_search = get_gbif_search()

    # First columns get handled differently in some outputs. See module doc string
    first_columns = {
        image_path: {
            "text": ocr_by_image[image_path]["text"],
            "image_path": image_path,
            "href": gbif["identifier"],
            "row_num": str(i),
        }
        for i, (image_path, gbif) in enumerate(gbif_by_image.items(), 1)
    }

    # Build report cells
    rows = []
    for image_path in image_paths:
        gbif_input = gbif_by_image[image_path]
        gbif_row = {"row_type": "GBIF"} | {c: [] for c in columns}
        llm_rows, score_rows = [], []
        for llm_file in args.llm_file:
            llm_row = {"row_type": llm_file.stem} | {
                c: llm_data[llm_file.stem][c] for c in column_keys
            }
            llm_rows.append(llm_row)
            score_row = {"row_type": f"{llm_file.stem} score"}
            for col in columns:
                actual = llm_row[col]
                score = calc_score(col, actual, gbif_input, gbif_search)
                score_row[col] = score
                if score.gbif_field:
                    gbif_row[col].append(score)
            score_rows.append(score_row)
        rows += [gbif_row, *llm_rows, *score_rows]

    match args.output_file.suffix.lower():
        case ".html":
            pass
            # write_html(
            #     html_file=args.output_file,
            #     columns=columns,
            #     row_groups=row_groups,
            #     row_span=len(llm_dicts) * 2 + 1,  # gbif + llm + score per file
            #     gbif_search=gbif_search,
            #     stats=stats,
            #     notes=args.notes,
            # )
        case ".ods":
            write_ods(
                ods_file=args.output_file,
                image_paths=image_paths,
                columns=columns,
                first_columns=first_columns,
                rows=rows,
                gbif_search=gbif_search,
                stats=stats,
            )

    log.finished()


def calc_score(col: str, actual: str, gbif_input: dict, gbif_search: dict) -> Score:
    expect = gbif_input[col]
    if expect:
        score = fuzz.partial_ratio(expect, actual) / 100.0
        return Score(
            cat=ScoreCat.gbif_has_value,
            score=score,
            method="FPR",
            gbif_field=col,
            gbif_data=expect,
        )

    if not actual:
        return Score(cat=ScoreCat.both_empty, method="NONE")

    max_score = (-1.0, 0)
    max_field, max_expect = "", ""

    for search_field in gbif_search.get(col, []):
        expect = gbif_input.get(search_field, "")
        if not expect:
            continue

        score = fuzz.partial_ratio(expect, gbif_input[search_field]) / 100.0
        if (score, -len(expect)) > max_score and score > 0.0:
            max_field = search_field
            max_expect = expect
            max_score = (score, -len(expect))

    if max_field:
        return Score(
            cat=ScoreCat.search_success,
            score=max_score[0],
            method="FPR",
            gbif_field=max_field,
            gbif_data=max_expect,
        )

    return Score(cat=ScoreCat.search_fail)


def write_ods(
    ods_file: Path,
    image_paths: list[str],
    columns: list[str],
    first_columns: dict,
    rows: list[dict],
    gbif_search: dict,
    stats: dict,
) -> None:
    stats_rows = []
    for stem, fields in stats.items():
        for col, data in fields.items():
            stats_rows.append({"file": stem, "column": col, **data})
    stats_df = pd.DataFrame(stats_rows)

    rows = []
    for image in image_paths:
        first = first_columns[image]
        gbif_row = first
        for col in columns:
            gbif_row[col]
        # gbif_row = {c: cell_groups[image][c].gbif_cell for c in columns}
        rows.append(first | gbif_row)
        for col in columns:
            row_group.append({col})

    # for group in row_groups:
    #     group_rows.append(group.gbif_row)
    #     group_rows += group.llm_rows
    #     group_rows += group.score_rows
    # group_df = pd.DataFrame(group_rows)

    # gbif_rows = [
    #     {"field": k, "search fields": ", ".join(v)} for k, v in gbif_search.items()
    # ]
    # gbif_df = pd.DataFrame(gbif_rows)

    # with pd.ExcelWriter(ods_file, engine="odf") as writer:
    #     stats_df.to_excel(writer, sheet_name="statistics", index=False)
    #     group_df.to_excel(writer, sheet_name="detail", index=False)
    #     gbif_df.to_excel(writer, sheet_name="gbif_search_fields", index=False)


# def write_html(
#     html_file: Path | str,
#     columns: list[str],
#     row_groups: list[RowGroup],
#     row_span: int,
#     gbif_search: dict,
#     stats: dict,
#     notes: str,
# ) -> None:

#     env = jinja2.Environment(
#         loader=jinja2.FileSystemLoader(Path(__file__).resolve().parent / "templates"),
#         autoescape=True,
#     )

#     template = env.get_template("compare_output_gbif.html").render(
#         now=datetime.now().strftime("%Y-%m-%d %H:%M"),
#         columns=columns,
#         headers=FIRST_COLUMNS + columns,
#         groups=row_groups,
#         row_span=row_span,
#         gbif_search=gbif_search,
#         stats=stats,
#         notes=notes,
#     )

#     with Path(html_file).open("w") as fout:
#         fout.write(template)


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
    score_against_gbif(ARGS)
