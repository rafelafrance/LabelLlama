#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path

import dspy
from pylib import darwin_core as dwc
from pylib import log
from rich.console import Console

from llama.label_types import label_types


def main(args: argparse.Namespace) -> None:
    log.started()

    label_type = label_types.LABEL_TYPES[args.label_type]

    console = Console()

    lm = dspy.LM(args.model, api_base=args.api_base, api_key=args.api_key, cache=False)
    dspy.configure(lm=lm)

    label_data = label_types.read_label_data(args.label_input)
    limit = args.limit if args.limit else len(label_data)
    label_data = label_data[:limit]

    extractor = dspy.Predict(label_type.signature)

    predictions = []

    for i, label in enumerate(label_data, 1):
        console.log(f"[blue]{'=' * 80}")
        console.log(f"[blue]{i} {label['path']}")
        console.log(f"[blue]{label['text']}")

        pred = extractor(text=label["text"], prompt=label_type.prompt)

        console.log(f"[green]{pred}")

        as_dict = {
            "path": label["path"],
            "text": label["text"],
            "annotations": dwc.to_dwc_keys(pred.toDict(), label_type.dwc),
        }

        predictions.append(as_dict)

    with args.annotations_json.open("w") as f:
        f.write(json.dumps(predictions, indent=4) + "\n")

    log.finished()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""
            Extract information from OCRed herbarium labels. I use this for:
            1. Inference.
            2. Bootstrapping annotation training data.
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
        "--label-input",
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
