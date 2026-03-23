#!/usr/bin/env python3

import argparse
import textwrap
from collections import defaultdict
from pathlib import Path

import Levenshtein
import pandas as pd

from llama.postprocess.all_fields import ALL_ACTIONS


def score(args: argparse.Namespace) -> None:
    gold_df = pd.read_csv(args.gold_tsv, sep="\t").fillna("")
    lm_df = pd.read_csv(args.lm_tsv, sep="\t").fillna("")

    gold_data = gold_df.to_dict("records")
    lm_data = lm_df.to_dict("records")

    compare = {r["src_path"]: [r] for r in gold_data}
    for row in lm_data:
        key = row["src_path"]
        if key in compare:
            compare[key].append(row)
    compare = [p for p in compare.values() if len(p) == 2]

    field_list = [c for c in ALL_ACTIONS if c in gold_df.columns and c in lm_df.columns]

    df_data: list[dict[str, str]] = []

    avg = defaultdict(float)

    for gold, lm in compare:
        row1: dict[str, str] = {
            "source": Path(gold["src_path"]).name,
            "doc_text": gold["doc_text"],
            "row": "gold",
        }
        row2: dict[str, str] = {
            "source": "",
            "doc_text": "",
            "row": "lm",
        }
        row3: dict[str, float | str] = {
            "source": "",
            "doc_text": "",
            "row": "score",
        }

        for field in field_list:
            row1[field] = gold.get(field, "")
            row2[field] = lm.get(field, "")
            row3[field] = Levenshtein.ratio(row1[field], row2[field])
            avg[field] += row3[field]

        df_data += [row1, row2, row3]

    df = pd.DataFrame(df_data).fillna("")
    df.to_csv(args.output_tsv, sep="\t", index=False)

    for field, score in avg.items():
        print(f"{field},{score / len(gold_data):0.2f}")


# ------------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Score a language model job against a gold standard."""
        ),
    )
    arg_parser.add_argument(
        "--gold-tsv",
        type=Path,
        required=True,
        help="""The gold standard to score againt.""",
    )
    arg_parser.add_argument(
        "--lm-tsv",
        type=Path,
        required=True,
        help="""The LM data to score.""",
    )
    arg_parser.add_argument(
        "--output-tsv",
        type=Path,
        required=True,
        help="""Write the results to this file.""",
    )

    # ------------------------------------------------------------
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    score(ARGS)
