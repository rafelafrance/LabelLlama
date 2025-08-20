#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path
from pprint import pp

import dspy
from extractors import herbarium_extractor as ie
from pylib import darwin_core as dwc
from pylib import log
from rich import print as rprint


def main(args: argparse.Namespace) -> None:
    log.started()

    with args.ocr_jsonl.open() as f:
        labels = [json.loads(ln) for ln in f]
    labels = labels[: args.limit] if args.limit else labels

    lm = dspy.LM(
        args.model, api_base=args.api_base, api_key=args.api_key, cache=args.no_cache
    )
    dspy.configure(lm=lm)

    trait_extractor = dspy.Predict(ie.HerbariumExtractor)

    predictions = []

    for i, label in enumerate(labels, 1):
        rprint(f"[blue]{'=' * 80}")
        rprint(f"[blue]{i} {label['metadata']['Source-File']}")
        rprint(f"[blue]{label['text']}")
        print()

        pred = trait_extractor(text=label["text"], prompt=ie.PROMPT)

        rprint(f"[green]{pred}")

        as_dict = {
            "Source-File": label["metadata"]["Source-File"],
            "text": label["text"],
            "annotations": dwc.rekey(pred.toDict()),
        }
        pp(as_dict)

        predictions.append(as_dict)

    if args.predictions_json:
        with args.predictions_json.open("w") as f:
            f.write(json.dumps(predictions, indent=4) + "\n")

    log.finished()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("Extract information from OCRed herbarium labels."),
    )

    arg_parser.add_argument(
        "--ocr-jsonl",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Get OCR results from this JSONL file.""",
    )

    arg_parser.add_argument(
        "--predictions-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output LLM predictions to this file.""",
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
