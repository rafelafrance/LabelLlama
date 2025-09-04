#!/usr/bin/env python3

import argparse
import random
import textwrap
from collections.abc import Callable
from pathlib import Path

import dspy
from dspy.evaluate import Evaluate
from dspy.evaluate.evaluate import EvaluationResult
from dspy.teleprompt import BootstrapFewShotWithRandomSearch
from model_data import herbarium_label as he
from pylib import log
from rich.console import Console
from rich.table import Table

from llama.model_data import label_types


def main(args: argparse.Namespace) -> None:
    log.started(args=args)

    label_type = label_types.LABEL_TYPES[args.label_type]

    console = Console()

    lm = dspy.LM(args.model, api_base=args.api_base, api_key=args.api_key, cache=False)
    dspy.configure(lm=lm)

    random.seed(args.seed)

    label_data = label_types.read_label_data(args.gold_json)
    limit = args.limit if args.limit else len(label_data)
    label_data = random.sample(label_data, limit)

    examples = [label_types.dict2example(lb, label_type) for lb in label_data]

    train_set, val_set, test_set = label_types.split_examples(
        examples, train_split=args.train_split, val_split=args.val_split
    )

    initial_program = dspy.Predict(he.HerbariumLabel)
    initial_score = evaluate_program(
        initial_program, test_set, label_types.levenshtein_score
    )
    console.log(f"[bold blue]Initial score: {initial_score}")

    console.log("[bold green]Running optimization")

    optimizer = None
    match args.optimizer:
        case "miprov2":
            optimizer = dspy.MIPROv2(
                metric=label_types.levenshtein_score,
                auto="medium",
                verbose=True,
            )

        case "random_search":
            optimizer = BootstrapFewShotWithRandomSearch(
                metric=label_types.levenshtein_score,
                max_bootstrapped_demos=4,
                max_labeled_demos=4,
                num_candidate_programs=10,
                num_threads=4,
            )

    optimized_program = optimizer.compile(
        initial_program,
        trainset=train_set,
        valset=val_set,
    )

    optimized_score = evaluate_program(
        optimized_program, test_set, label_types.levenshtein_score
    )
    console.log(f"[bold blue]Optimized score: {optimized_score}")
    improvement = optimized_score - initial_score

    relative_improvement = (
        (improvement / initial_score * 100) if initial_score > 0 else 0
    )

    results_table = Table(title="Performance Comparison")
    results_table.add_column("Metric", style="cyan")
    results_table.add_column("Score", justify="right")

    results_table.add_row("Initial Program", f"{initial_score:.4f}")
    results_table.add_row("Optimized Program", f"{optimized_score:.4f}")
    results_table.add_row("Improvement", f"{improvement:+.4f}")
    results_table.add_row("Relative Improvement", f"{relative_improvement:+.2f}%")

    console.print(results_table)

    optimized_program.save(args.optimized)

    log.finished()


def evaluate_program(
    program: dspy.Predict,
    dataset: list[dspy.Example],
    metric: Callable,
) -> EvaluationResult:
    evaluator = Evaluate(
        devset=dataset,
        num_threads=1,
        display_progress=True,
        display_table=True,
        provide_traceback=True,
    )
    score = evaluator(program, metric=metric)
    return score


def validate_splits(args: argparse.Namespace) -> None:
    splits = (args.train_split, args.val_split, args.test_split)

    if sum(splits) != 1.0:
        msg = "train, val, and test splits must sum to 1.0"
        raise ValueError(msg)

    if any(s < 0.0 or s > 1.0 for s in splits):
        msg = "All splits must be in the interval [0.0, 1.0]"
        raise ValueError(msg)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("Train a nodel with given examples."),
    )

    choices = list(label_types.LABEL_TYPES.keys())
    arg_parser.add_argument(
        "--label-type",
        choices=choices,
        default=choices[0],
        help="""Use this label model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--gold-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Get gold standard annotations from this JSON file.""",
    )

    arg_parser.add_argument(
        "--model",
        default="ollama_chat/gemma3:27b",
        help="""Use this LLM model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--optimizer",
        choices=["miprov2", "random_search", "finetune"],
        default="miprov2",
        help="""Use this LLM model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--optimized",
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
        default=830035,
        help="""Seed for the random number generator. (default: %(default)s)""",
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
