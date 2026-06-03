#!/usr/bin/env python3

import argparse
import logging
import textwrap
from collections import defaultdict
from pathlib import Path

from llama.fields.base_field import BaseField
from llama.pylib import io_util, log, prompt_util

PAIR: int = 2


def score_extracts(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    gold_df = io_util.read_to_df(args.gold_file)
    lm_df = io_util.read_to_df(args.lm_file)

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

    skips = ["source", "text", "index"]
    columns = [c for c in gold_df.columns if c in lm_df.columns and c not in skips]

    field_list = prompt_util.read_field_list(args.prompt)
    field_classes = prompt_util.field_classes_by_column_name(field_list)

    rows = []
    df_rows = []
    avg = defaultdict(float)

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
            "type": args.gold_file.stem,
        }
        df_row3: dict[str, str] = {
            "source": "",
            "text": "",
            "row": "",
            "type": args.lm_file.stem,
        }
        df_row4: dict[str, float | str] = {
            "source": "",
            "text": "",
            "row": "",
            "type": "score",
        }

        for column in columns:
            expect = gold.get(column)
            actual = lm.get(column)

            field_action = field_classes.get(column, BaseField)
            score = field_action.score(expect, actual, lm)

            df_row1[column] = ""
            df_row2[column] = str(expect)
            df_row3[column] = str(actual)
            df_row4[column] = score

            avg[column] += score

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
        "--prompt",
        type=Path,
        required=True,
        help="""A markdown file with a prompt and list of fields to parse.
            It is used to get the correct version of the scoring modules.""",
    )
    arg_parser.add_argument(
        "--gold-file",
        type=Path,
        required=True,
        help="""The one of the files to compare.""",
    )
    arg_parser.add_argument(
        "--lm-file",
        type=Path,
        required=True,
        help="""The one of the files to compare.""",
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
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    score_extracts(ARGS)
