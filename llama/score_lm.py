#!/usr/bin/env python3

import argparse
import json
import textwrap
from dataclasses import asdict
from pathlib import Path

import dspy
from pylib import herbarium_extractor as ie
from pylib import log
from pylib import track_scores as ts
from rich import print as rprint


def main(args):
    log.started(args=args)

    label_data = ie.read_label_data(args.gold_json)
    label_data = label_data[: args.limit] if args.limit else label_data

    lm = dspy.LM(
        args.model, api_base=args.api_base, api_key=args.api_key, cache=args.no_cache
    )
    dspy.configure(lm=lm)

    trait_extractor = dspy.Predict(ie.HerbariumExtractor)

    scores = []

    for i, one_label in enumerate(label_data, 1):
        example = ie.dict2example(one_label)

        rprint(f"[blue]{i} / {len(label_data)} {'=' * 80}")
        rprint(f"[blue]{example['text']}")
        print()

        pred = trait_extractor(text=example["text"], prompt=ie.PROMPT)

        score = ts.TrackScores.track_scores(example=example, prediction=pred)
        score.display()

        score = {
            "Source-File": one_label["Source-File"],
            "text": one_label["text"],
            **asdict(score),
        }

        scores.append(score)

    ts.TrackScores.summarize_scores(scores)

    if args.score_json:
        with args.score_json.open("w") as f:
            json.dump(scores, f, indent=4)

    log.finished()


def parse_args():
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("Extract information from OCRed herbarium labels."),
    )

    arg_parser.add_argument(
        "--gold-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Get gold standard from this JSON file.""",
    )

    arg_parser.add_argument(
        "--score-json",
        type=Path,
        metavar="PATH",
        help="""Save score results to this JSON file.""",
    )

    arg_parser.add_argument(
        "--model",
        default="ollama_chat/gemma3:27b",
        help="""Use this LLM model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--api-base",
        default="http://localhost:11434",
        help="""URL for the LM model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--api-key",
        help="""Key for the LM provider.""",
    )

    arg_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="""Turn off caching for the model.""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        default=0,
        metavar="INT",
        help="""Limit to this many labels, 0 = all (default: %(default)s)""",
    )

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
