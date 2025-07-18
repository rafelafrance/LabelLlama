#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

import dspy
from pylib import info_extractor as ie
from pylib import log
from pylib import track_scores as ts
from rich import print as rprint


def main(args):
    log.started()

    examples = ie.read_labels(args.gold_json, args.limit)

    lm = dspy.LM(
        args.model, api_base=args.api_base, api_key=args.api_key, cache=args.no_cache
    )
    dspy.configure(lm=lm)

    trait_extractor = dspy.Predict(ie.InfoExtractor)

    scores = []

    for i, example in enumerate(examples, 1):
        rprint(f"[blue]{i} {'=' * 80}")
        rprint(f"[blue]{example['text']}")
        print()

        pred = trait_extractor(text=example["text"], prompt=ie.PROMPT)

        score = ts.TrackScores.track_scores(example=example, prediction=pred)
        score.display()

        scores.append(score)

    ts.TrackScores.summarize_scores(scores)

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
