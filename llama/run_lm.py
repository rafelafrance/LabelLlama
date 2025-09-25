#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

from llama.data_formats import label_types
from llama.model_utils.extract_dwc import extract_info


def main(args: argparse.Namespace) -> None:
    extract_info(args)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""
            Extract information from OCRed museum labels. I use this for:
            1. Inference.
            2. Bootstrapping annotation training data.
            3. Various data tests and demonstrations.
            """),
    )

    choices = list(label_types.LABEL_TYPES.keys())
    arg_parser.add_argument(
        "--label-type",
        choices=choices,
        default=choices[0],
        help="""Use this label model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--label-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Get label data from this JSON file.""",
    )

    arg_parser.add_argument(
        "--annotations-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output predicted annotations to this JSON file.""",
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
