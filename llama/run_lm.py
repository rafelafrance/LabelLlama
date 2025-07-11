#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path

import dspy
from pylib import info_extractor as te
from pylib import log
from rich import print as rprint

# from pprint import pp
# from pylib import track_scores as ts


def main(args):
    log.started()

    with args.ocr_jsonl.open() as f:
        labels = [json.loads(ln) for ln in f]
    labels = labels[: args.limit] if args.limit else labels

    lm = dspy.LM(
        args.model, api_base=args.api_base, api_key=args.api_key, cache=args.no_cache
    )
    dspy.configure(lm=lm)

    trait_extractor = dspy.Predict(te.InfoExtractor)
    # trait_extractor = dspy.ChainOfThought(TraitExtractor)

    preds = []

    for i, label in enumerate(labels, 1):
        rprint(f"[blue]{'=' * 80}")
        rprint(f"[blue]{i} {label['metadata']['Source-File']}")
        rprint(f"[blue]{label['text']}")
        print()

        pred = trait_extractor(text=label["text"], prompt=te.PROMPT)

        rprint(f"[green]{pred}")

        # score = ts.TrackScores.track_scores(label=label, prediction=pred)
        # score.display()

        as_dict = {
            "Source-File": label["metadata"]["Source-File"],
            "text": label["text"],
        }
        as_dict |= pred.toDict()

        preds.append(as_dict)

    # ts.TrackScores.summarize_scores(scores)

    if args.predictions_jsonl:
        with args.predictions_jsonl.open("w") as f:
            for pred in preds:
                f.write(json.dumps(pred) + "\n")

    log.finished()


def parse_args():
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

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
