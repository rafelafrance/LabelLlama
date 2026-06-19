#!/usr/bin/env python3

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
class Accum:
    field_in_gbif: dict = field(
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
        stats = defaultdict(lambda: defaultdict(dict))
        for llm_file in llm_files:
            stem = llm_file.stem
            for col in columns:
                count, avg = "", ""
                if self.field_in_gbif.get(stem) and self.field_in_gbif[stem].get(col):
                    values = self.field_in_gbif[stem][col]
                    count = str(len(values))
                    avg = f"{sum(values) / len(values):0.2f}"
                stats[stem][col]["field_in_gbif_count"] = count
                stats[stem][col]["field_in_gbif_average"] = avg

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
class Group:
    gbif_row: dict = field(default_factory=dict)
    llm_rows: list[dict] = field(default_factory=list)
    score_rows: list[dict] = field(default_factory=list)


def main(args: argparse.Namespace) -> None:
    """Compare LLM outputs against gbif data and write an HTML report."""
    log.started(args.log_file, args=args)

    # ocr data
    ocr_df = io_util.read_to_df(args.ocr_file)
    ocr_dict = {o["source"]: o for o in ocr_df.to_dict("records")}

    # Load data
    gbif_df = io_util.read_to_df(args.gbif_file)
    gbif_dict = {g["source"]: g for g in gbif_df.to_dict("records")}

    sources = set(gbif_dict)
    columns = {}

    llm_dicts = {}
    for llm_file in args.llm_file:
        llm_df = io_util.read_to_df(llm_file)
        llm_dict = {r["source"]: r for r in llm_df.to_dict("records")}
        key = llm_file.stem
        llm_dicts[key] = llm_dict
        sources &= set(llm_dict)
        columns |= dict.fromkeys(llm_df.columns)

    sources = sorted(sources)
    sources = sources[: args.limit] if args.limit else sources

    columns = [k for k in columns if k not in FIRST_COLUMNS]

    aligned = set(gbif_df.columns) & set(columns)
    gbif_search = get_gbif_search()

    accum = Accum()
    groups = []

    for i, source in tqdm(enumerate(sources, 1), total=len(sources)):
        gbif = gbif_dict[source]

        # Build gbif row
        group = Group(
            gbif_row={
                "text": ocr_dict.get(source, {}).get("text", ""),
                "source": gbif["source"],
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
                    col, llm_dict[source], gbif, gbif_search, accum, stem
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

    write_template(
        args.html_file,
        columns,
        groups,
        len(llm_dicts) * 2 + 1,
        gbif_search,
        accum,
        args.llm_file,
        args.notes,
    )

    log.finished()


def calc_score(
    field: str,
    llm_dict: dict,
    gbif: dict,
    gbif_search: dict,
    accum: Accum,
    stem: str,
) -> tuple[str, str | None]:
    actual = llm_dict[field]

    if field in gbif:
        score = fuzz.partial_ratio(gbif[field], actual) / 100.0
        accum.field_in_gbif[stem][field].append(score)
        return f"FPR: {score:0.2f}", None

    if not actual:
        accum.field_empty[stem][field].append(1)
        return "NONE: 1.0", None

    max_score = (-1.0, 0)
    max_field, max_expect = "", ""

    for search_field in gbif_search.get(field, []):
        expect = gbif.get(search_field, "")
        if not expect:
            continue
        score = fuzz.partial_ratio(expect, actual) / 100.0
        if (score, -len(expect)) > max_score and score > 0.0:
            max_field = search_field
            max_score = (score, -len(expect))
            max_expect = expect

    if max_field:
        accum.search_success[stem][field].append(max_score[0])
    else:
        accum.search_fail[stem][field].append(1)

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
    groups: list[Group],
    row_span: int,
    gbif_search: dict,
    accum: Accum,
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
        groups=groups,
        row_span=row_span,
        gbif_search=gbif_search,
        stats=accum.format(llm_files, columns),
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
            burried in the "locality" field in GBIF but it may be broken into
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
    main(ARGS)
