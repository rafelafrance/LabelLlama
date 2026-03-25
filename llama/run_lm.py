#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

import dspy
import pandas as pd

from llama.common import log
from llama.lm.all_signatures import SIGNATURES
from llama.lm.dwc_module import DwcModule


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
    parallel = dspy.Parallel(num_threads=args.threads)

    docs = pd.read_csv(args.doc_tsv, sep="\t").fillna("").to_dict("records")
    docs = docs[: args.limit]
    exec_pairs = [(predictor, {"text": d["text"], "source": d["source"]}) for d in docs]

    results = parallel(exec_pairs)

    df = pd.DataFrame(results)
    df.to_csv(args.lm_tsv, sep="\t", index=False)

    log.finished()


# ----------------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Use a language model (LM) to extract information from text."""
        ),
    )
    signatures = list(SIGNATURES.keys())
    arg_parser.add_argument(
        "--signature",
        choices=signatures,
        default=signatures[0],
        help="""What type of data are you extracting? What is its signature?""",
    )
    arg_parser.add_argument(
        "--doc-tsv",
        type=Path,
        help="""Parse doc records from this TSV file.""",
    )
    arg_parser.add_argument(
        "--lm-tsv",
        type=Path,
        help="""Write the LM results to this TSV file.""",
    )
    arg_parser.add_argument(
        "--threads",
        type=int,
        default=10,
        help="""How many parallel threads to run. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--model-name",
        default="lm_studio/google/gemma-3-27b",
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
        default=65536,
        help="""Model's context length. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--temperature",
        type=float,
        help="""Model's temperature. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="""Don't use cached records?""",
    )
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        help="""Append logging notices to this file.""",
    )
    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the number of records to parse.""",
    )
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    lm_extraction(ARGS)
