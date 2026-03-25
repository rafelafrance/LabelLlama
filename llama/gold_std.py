#!/usr/bin/env python3

import argparse
import textwrap
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import Levenshtein
import pandas as pd

from llama.common import log
from llama.postprocess.all_fields import ALL_ACTIONS


@dataclass
class FieldScore:
    field: str
    expect: Any
    actual: Any = None
    edit_dist: float = 0.0
    fuzzy_score: float = 0.0
    cross_field: float = 0.0

    @property
    def score(self) -> float:
        return max(self.edit_dist, self.fuzzy_score, self.cross_field)


@dataclass
class Row:
    source: str
    text: str
    edit_dist: float | None = None
    scores: list[FieldScore] = field(default_factory=list)
    actual_record: dict[str, Any] = field(default_factory=dict)


def score_extracts(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    gold_df = pd.read_csv(args.gold_tsv, sep="\t").fillna("")
    lm_df = pd.read_csv(args.lm_tsv, sep="\t").fillna("")

    gold_data = gold_df.to_dict("records")
    lm_data = lm_df.to_dict("records")

    compare = {r["source"]: [r] for r in gold_data}
    for row in lm_data:
        key = row["source"]
        if key in compare:
            compare[key].append(row)
    compare = [p for p in compare.values() if len(p) == 2]

    field_list = [c for c in ALL_ACTIONS if c in gold_df.columns and c in lm_df.columns]

    for field_name in field_list:
        ALL_ACTIONS[field_name].setup_field()

    rows = []
    df_rows = []
    avg = defaultdict(float)

    # Build field data and get edit distance scores
    for gold, lm in compare:
        row = Row(source=gold["source"], text=gold["text"], actual_record=lm)
        rows.append(row)

        df_row1: dict[str, str] = {
            "source": Path(gold["source"]).name,
            "text": gold["text"],
            "row": "gold",
        }
        df_row2: dict[str, str] = {
            "source": "",
            "text": "",
            "row": "lm",
        }
        df_row3: dict[str, float | str] = {
            "source": "",
            "text": "",
            "row": "score",
        }

        for field_name in field_list:
            expect = gold.get(field_name, "")
            actual = lm.get(field_name, "")

            field_action = ALL_ACTIONS[field_name]

            field_score = FieldScore(
                field=field_name,
                expect=expect,
                actual=actual,
                edit_dist=Levenshtein.ratio(expect, actual),
                fuzzy_score=field_action.fuzzy_score(expect, actual),
                cross_field=field_action.cross_field_score(
                    expect, actual, row.actual_record
                ),
            )

            df_row1[field_name] = expect
            df_row2[field_name] = actual
            df_row3[field_name] = field_score.score

            avg[field_name] += field_score.score

        df_rows += [df_row1, df_row2, df_row3]

    avg_row: dict[str, float | str] = {
        "source": "",
        "text": "",
        "row": "avg",
    }
    df_rows.append(avg_row)

    df = pd.DataFrame(df_rows).fillna("")
    df.to_csv(args.output_tsv, sep="\t", index=False)

    for field_name, score in avg.items():
        print(f"{field_name},{score / len(gold_data):0.2f}")

    log.finished()


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
        help="""The gold standard to score against.""",
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
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        help="""Append logging notices to this file.""",
    )
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    score_extracts(ARGS)
