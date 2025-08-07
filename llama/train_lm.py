#!/usr/bin/env python3

import argparse
import random
import textwrap
from pathlib import Path

import dspy
from dspy.evaluate import Evaluate
from pylib import info_extractor as ie
from pylib import log


def main(args):
    log.started(args=args)

    random.seed(args.seed)

    label_data = ie.read_label_data(args.gold_json, args.limit)
    examples = [ie.dict2example(lb) for lb in label_data]

    dataset = ie.split_examples(
        examples, train_split=args.train_split, val_split=args.val_split
    )

    lm = dspy.LM(
        args.model, api_base=args.api_base, api_key=args.api_key, cache=args.no_cache
    )
    dspy.configure(lm=lm)
    info_extractor = dspy.Predict(ie.InfoExtractor)

    evaluator = Evaluate(
        devset=dataset["dev"],
        metric=ie.score_prediction,
        num_threads=1,
        display_progress=True,
        display_table=True,
        provide_traceback=True,
    )

    evaluator(info_extractor, devset=dataset["dev"])

    mipro_optimizer = dspy.MIPROv2(metric=ie.score_prediction, auto="medium")

    optimized_info_extractor = mipro_optimizer.compile(
        info_extractor,
        trainset=dataset["train"],
        max_bootstrapped_demos=4,
        requires_permission_to_run=False,
        minibatch=False,
    )

    evaluator(optimized_info_extractor, devset=dataset["dev"])

    dspy.inspect_history(n=1)

    optimized_info_extractor.save(args.prompts_json)

    log.finished()


def validate_splits(args: argparse.Namespace) -> None:
    splits = (args.train_split, args.val_split, args.test_split)

    if sum(splits) != 1.0:
        msg = "train, val, and test splits must sum to 1.0"
        raise ValueError(msg)

    if any(s < 0.0 or s > 1.0 for s in splits):
        msg = "All splits must be in the interval [0.0, 1.0]"
        raise ValueError(msg)


def parse_args():
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("Train a nodel with given examples."),
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
        "--prompts-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Save updated model prompts to this JSON file.""",
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
        "--train-split",
        type=float,
        metavar="FRACTION",
        default=0.3,
        help="""What fraction of records to use for training the model.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--val-split",
        type=float,
        metavar="FRACTION",
        default=0.4,
        help="""What fraction of records to use for validating the model between epochs.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--test-split",
        type=float,
        metavar="FRACTION",
        default=0.3,
        help="""What fraction of records to use for testing the model.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--seed",
        type=int,
        metavar="INT",
        default=839935,
        help="""Seed for the random number generator. (default: %(default)s)""",
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
    validate_splits(args)

    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
