#!/usr/bin/env python3

import argparse
import logging
import textwrap
from pathlib import Path

import dspy

from llama.common import io_util, log
from llama.lm.all_signatures import ALL_SIGNATURES
from llama.lm.dwc_module import DwcModule
from llama.lm.preprocess import clean_text


def lm_extraction(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    lm = dspy.LM(
        args.model_name,
        api_base=args.api_host,
        api_key=args.api_key,
        temperature=args.temperature,
        max_tokens=args.context_length,
        cache=not args.no_cache,
    )
    dspy.configure(lm=lm)

    predictor = DwcModule(args.signature)

    # Record the prompt for later use
    if args.log_file:
        prompt = dspy.ChatAdapter().format_system_message(predictor.signature)
        logging.info(prompt)

    parallel = dspy.Parallel(num_threads=args.threads)

    docs = io_util.read_list_of_dicts(args.doc_in, fill_na="", limit=args.limit)

    exec_pairs = [
        (predictor, {"text": clean_text(d["text"]), "source": d["source"]})
        for d in docs
    ]

    results = parallel(exec_pairs)

    io_util.output_file(args.out_file, results)

    log.finished()


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Use a language model (LM) to extract information from text."""
        ),
    )
    signatures = list(ALL_SIGNATURES.keys())
    arg_parser.add_argument(
        "--signature",
        choices=signatures,
        default=signatures[0],
        help="""What type of data are you extracting? What is its signature?""",
    )
    arg_parser.add_argument(
        "--doc-in",
        type=Path,
        help="""Parse doc text from this file. We need only 'source' and 'text'
            columns for valid input, so any file with those columns are fine.""",
    )
    arg_parser.add_argument(
        "--out-file",
        type=Path,
        help="""Write the LM results to this file.
           Handles (.json, .jsonl, .csv, .tsv)""",
    )
    arg_parser.add_argument(
        "--threads",
        type=int,
        default=10,
        help="""How many parallel threads to run. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--model-name",
        default="lm_studio/google/gemma-4-26b-a4b",
        help="""Use this language model. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--api-host",
        # default="http://localhost:1234/v1",
        help="""URL for the LM model.""",
    )
    arg_parser.add_argument(
        "--api-key",
        help="""API key.""",
    )
    arg_parser.add_argument(
        "--context-length",
        type=int,
        help="""Model's context length.""",
    )
    arg_parser.add_argument(
        "--max-tokens",
        type=int,
        help="""Model's max tokens for output.""",
    )
    arg_parser.add_argument(
        "--temperature",
        type=float,
        help="""Model's temperature.""",
    )
    arg_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="""Don't use cached records?""",
    )
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    lm_extraction(ARGS)
