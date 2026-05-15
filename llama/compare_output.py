#!/usr/bin/env python3

import argparse
import logging
import textwrap
from collections import defaultdict
from pathlib import Path

from rich import print as rprint

from llama.fields.base_field import BaseField
from llama.pylib import io_util, log, prompt_util, score_util

PAIR: int = 2


def score_extracts(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    gold_df = io_util.read_to_df(args.gold)
    lm_df = io_util.read_to_df(args.lm)

    gold_data = gold_df.fillna("").to_dict("records")
    lm_data = lm_df.fillna("").to_dict("records")

    compare = {r["source"]: [r] for r in gold_data}
    for row in lm_data:
        key = row["source"]
        if key in compare:
            compare[key].append(row)

    for key, cmp in compare.items():
        if len(cmp) != PAIR:
            logging.warning(f"'{key}' did not have a pair of rows to compare")

    compare = [p for p in compare.values() if len(p) == PAIR]

    skips = ["source", "text"]
    field_list = [c for c in gold_df.columns if c in lm_df.columns and c not in skips]
    field_list = args.column or field_list
    field_classes = prompt_util.get_field_classes(field_list)

    rows = []
    df_rows = []
    avg = defaultdict(float)

    # Build field data and get edit distance scores
    for i, (gold, lm) in enumerate(compare, 1):
        source = gold["source"]
        row = {"row": i, "source": source, "text": gold.get("text", lm["text"])}
        rows.append(row)

        df_row1: dict[str, str] = {
            "source": gold["source"],
            "text": gold.get("text", lm["text"]),
            "row": str(i),
            "type": "doc",
        }
        df_row2: dict[str, str] = {
            "source": "",
            "text": "",
            "row": "",
            "type": "gold",
        }
        df_row3: dict[str, str] = {
            "source": "",
            "text": "",
            "row": "",
            "type": "lm",
        }
        df_row4: dict[str, float | str] = {
            "source": "",
            "text": "",
            "row": "",
            "type": "score",
        }

        for field_name in field_list:
            expect = gold.get(field_name)
            actual = lm.get(field_name)

            field_action = field_classes.get(field_name, BaseField)
            score = field_action.score(expect, actual, lm)

            df_row1[field_name] = ""
            df_row2[field_name] = str(expect)
            df_row3[field_name] = str(actual)
            df_row4[field_name] = score

            avg[field_name] += score

            if debugging(args) and (args.imperfect and score != 1.0):
                print_debug_info(i, source, field_name, str(expect), str(actual), score)

        df_rows += [df_row1, df_row2, df_row3, df_row4]

    avg_row: dict[str, float | str] = {
        "index": "",
        "source": "",
        "text": "",
        "row": "average",
    }

    for field_name, score in avg.items():
        norm = score / len(gold_data)
        avg_row[field_name] = f"{norm:0.2f}"
        logging.info(f"{field_name:>28}: {norm:0.2f}")

    df_rows.append(avg_row)

    io_util.output_file(args.out_file, df_rows)

    log.finished()


def debugging(args: argparse.Namespace) -> bool:
    return args.column or args.limit


def print_debug_info(
    i: int, source: str, field_name: str, expect: str, actual: str, score: float
) -> None:
    color = score_util.score_color(score)
    rprint(f"{i} {source}")
    rprint(f"[{color}]{field_name}[/{color}]")
    rprint(f"[{color}]expect: {expect}[/{color}]")
    rprint(f"[{color}]actual: {actual}[/{color}]")
    print()


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Compare the outputs of two language model (LM) runs. One run is typically
            a gold standard, but this is not a requirement, and you may want to compare
            LM outputs for various reasons.""",
        ),
    )
    arg_parser.add_argument(
        "--gold",
        type=Path,
        required=True,
        help="""The gold standard to score against.""",
    )
    arg_parser.add_argument(
        "--lm",
        type=Path,
        required=True,
        help="""The LM data to score.""",
    )
    arg_parser.add_argument(
        "--out-file",
        type=Path,
        help="""Write the comparison results to this file.
           Handles (.json, .jsonl, .csv, .tsv, .html)""",
    )
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    arg_parser.add_argument(
        "--notes",
        help="""Notes for logging.""",
    )
    arg_parser.add_argument(
        "--column",
        action="append",
        help="""Just parse one column. Used for debugging.""",
    )
    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit to this many records. Used for debugging.""",
    )
    arg_parser.add_argument(
        "--imperfect",
        action="store_true",
        help="""Only show imperfect records. Used for debugging.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    score_extracts(ARGS)
