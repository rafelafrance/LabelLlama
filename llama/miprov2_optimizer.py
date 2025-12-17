#!/usr/bin/env python3

import argparse
import random
import textwrap
from pathlib import Path

import dspy
import duckdb

from llama.modules.dwc_extract import DwcExtract
from llama.pylib.metric import metric
from llama.signatures.all_signatures import SIGNATURES


def miprov2_dwc(args: argparse.Namespace) -> None:
    lm = dspy.LM(
        model=args.model_name,
        api_base=args.api_host,
        api_key=args.api_key,
        temperature=args.temperature,
        max_tokens=args.context_length,
        cache=args.cache,
    )
    dspy.configure(lm=lm)

    predictor = DwcExtract(args.signature)

    dataset: dict[str, list[dspy.Example]] = select_records(
        args.db_path,
        args.gold_run_id,
        predictor,
        train_split=args.train_fract,
        val_split=args.val_fract,
        limit=args.limit,
        seed=args.seed,
    )

    evaluator = dspy.evaluate.Evaluate(
        devset=dataset["trainval"],
        metric=metric,
        display_progress=True,
        provide_traceback=True,
    )

    evaluator(predictor, devset=dataset["trainval"])

    optimizer = dspy.MIPROv2(
        metric=metric,
        auto="medium",
    )

    compiled_model = optimizer.compile(
        student=predictor,
        trainset=dataset["train"],
        valset=dataset["val"],
        max_bootstrapped_demos=4,
        requires_permission_to_run=False,
        minibatch=False,
    )

    evaluator(compiled_model)
    dspy.inspect_history(n=1)
    compiled_model.save(args.optimized_json)


def select_records(
    db_path: Path,
    gold_run_id: int,
    predictor: dspy.Module,
    train_split: float = 0.1,
    val_split: float = 0.5,
    limit: int | None = None,
    seed: int = 992573,
) -> dict[str, list[dspy.Example]]:
    names = ", ".join(f"{f}" for f in predictor.output_names)

    sql = f"""
        select ocr_text as text, {names}
            from gold join ocr using (ocr_id)
            where gold_run_id = {gold_run_id}
        """
    if limit:
        sql += f" limit {limit}"

    with duckdb.connect(db_path) as cxn:
        df = cxn.execute(sql).pl()

    rows = df.rows(named=True)
    rows = [predictor.dict2example(r) for r in rows]

    random.seed(seed)
    random.shuffle(rows)

    total = len(rows)
    split1 = round(total * train_split)
    split2 = split1 + round(total * val_split)

    return {
        "train": rows[:split1],
        "val": rows[split1:split2],
        "test": rows[split2:],
        "trainval": rows[:split2],
    }


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Use MIPROv2 to optimize a model."""),
    )

    sigs = list(SIGNATURES.keys())
    arg_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
    )

    arg_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )

    arg_parser.add_argument(
        "--optimized-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Where to save the optimized prompt.""",
    )

    arg_parser.add_argument(
        "--gold-run-id",
        type=int,
        required=True,
        help="""Use this gold standard for scoring.""",
    )

    arg_parser.add_argument(
        "--model-name",
        default="lm_studio/google/gemma-3-27b",
        help="""Use this language model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--api-host",
        default="http://localhost:1234/v1",
        help="""URL for the LM model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--api-key",
        help="""API key.""",
    )

    arg_parser.add_argument(
        "--context-length",
        type=int,
        default=4096,
        help="""Model's context length. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="""Model's temperature. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        help="""Notes about this dataset.""",
    )

    arg_parser.add_argument(
        "--cache",
        action="store_true",
        help="""Use cached records?""",
    )

    arg_parser.add_argument(
        "--train-fract",
        type=float,
        default=0.1,
        metavar="FLOAT",
        help="""What fraction of the records to use for training.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--val-fract",
        type=float,
        default=0.5,
        metavar="FLOAT",
        help="""What fraction of the records to use for valiation.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the number of records to parse?""",
    )

    arg_parser.add_argument(
        "--seed",
        type=int,
        default=992573,
        help="""Seed for the random number generator. (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    miprov2_dwc(ARGS)
