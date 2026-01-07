#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path
from typing import LiteralString

import dspy
import duckdb

from llama.modules.dwc_extract import DwcExtract
from llama.pylib.const import SPLITS
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

    dataset: dict[LiteralString, list[dspy.Example]] = select_records(
        args.db_path, args.gold_run_id, predictor, args.signature
    )

    evaluator = dspy.evaluate.Evaluate(
        devset=dataset["val"],
        metric=metric,
        display_progress=True,
        provide_traceback=True,
    )

    evaluator(predictor, devset=dataset["val"])

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
    db_path: Path, gold_run_id: int, predictor: dspy.Module, signature: str
) -> dict[LiteralString, list[dspy.Example]]:
    names = ", ".join(f"{f}" for f in predictor.output_names)
    query = f"""
        select ocr_text as text, {names}
            from gold_{signature} join ocr using (ocr_id)
            where gold_run_id = ? and split = ?
        """

    with duckdb.connect(db_path) as cxn:
        splits: dict[LiteralString, list[dspy.Example]] = {}

        for split in SPLITS[:-1]:
            df = cxn.execute(query, [gold_run_id, split]).pl()
            splits[split] = [predictor.dict2example(r) for r in df.rows(named=True)]
            # splits[split] = splits[split][:3]  # ###################################

    return splits


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

    sigs = list(SIGNATURES.keys())
    arg_parser.add_argument(
        "--signature",
        choices=sigs,
        default=sigs[0],
        help="""What type of data are you extracting? What is its signature?""",
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

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    miprov2_dwc(ARGS)
