#!/usr/bin/env python3

import argparse
import io
import json
import textwrap
from datetime import datetime
from pathlib import Path

import dspy
from rich.console import Console

from llama.data_formats import specimen_types


def main(args: argparse.Namespace) -> None:
    console = Console(log_path=False)
    console.log("[blue]Started")
    job_started = datetime.now()

    specimen_type = specimen_types.SPECIMEN_TYPES[args.specimen_type]

    lm = dspy.LM(
        args.model_name,
        api_base=args.api_base,
        api_key=args.api_key,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        cache=args.cache,
    )
    dspy.configure(lm=lm)

    extractor = dspy.Predict(specimen_type.signature)

    ocr_records = []
    with args.ocr_input.open() as in_file:
        for ocr_ln in in_file:
            ocr_records.append(json.loads(ocr_ln))

    ocr_records = ocr_records[args.first : args.last]
    start = args.first if args.first else 0

    with args.dwc_output.open("a") as out_file:
        for i, ocr_rec in enumerate(ocr_records, start):
            rec_start = datetime.now()
            console.log(f"[blue]{i} {'=' * 80}")

            if ocr_rec.get("ocr_error"):
                console.log("[red] skipped due to ocr error")
                continue

            console.log(f"[blue]{ocr_rec['image_path']}")
            console.log(f"[blue]{ocr_rec['ocr_text']}")

            pred = extractor(text=ocr_rec["ocr_text"], prompt=specimen_type.prompt)
            console.log(f"[green]{pred}")
            append_result(out_file, ocr_rec, pred, args.model_name, args.ocr_input)
            console.log(f"[blue]Inference Time: {datetime.now() - rec_start}")

    console.log(f"[blue]Job Time: {datetime.now() - job_started}")
    console.log("[blue]Finished")


def append_result(
    out_file: io.StringIO,
    ocr_rec: dict,
    pred: dspy.Prediction,
    model_name: str,
    ocr_file: Path,
) -> dict:
    result = {
        **ocr_rec,
        "ocr_file": str(ocr_file),
        "dwc_model": model_name,
        "dwc_time": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "dwc_fields": pred.toDict(),
    }
    out_file.write(json.dumps(result))
    out_file.write("\n")
    out_file.flush()

    return result


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""
            Extract Darwin Core (DwC) information from text on museum specimens.
            """),
    )

    choices = list(specimen_types.SPECIMEN_TYPES.keys())
    arg_parser.add_argument(
        "--specimen-type",
        choices=choices,
        default=choices[0],
        help="""Use this specimen model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--ocr-input",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Parse OCR text from this JSONL file.""",
    )

    arg_parser.add_argument(
        "--dwc-output",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output predicted Darwin Core fields to this JSONL file.""",
    )

    arg_parser.add_argument(
        "--model-name",
        default="ollama_chat/gemma3:27b",
        help="""Use this language model. (default: %(default)s)
            also lm_studio/gemma-3-27b""",
    )

    arg_parser.add_argument(
        "--api-base",
        default="http://localhost:11434",
        help="""URL for the LM model. (default: %(default)s)
            ollama is http://localhost:11434 and lmstudio is http://localhost:1234""",
    )

    arg_parser.add_argument(
        "--api-key",
        help="""Key for the LM provider. Local ones do not need this.""",
    )

    arg_parser.add_argument(
        "--temperature",
        type=float,
        help="""Model temperature.""",
    )

    arg_parser.add_argument(
        "--max-tokens",
        type=int,
        help="""Maximum tokens.""",
    )

    arg_parser.add_argument(
        "--cache",
        action="store_true",
        help="""Use cached predictions?""",
    )

    arg_parser.add_argument(
        "--first",
        type=int,
        metavar="INT",
        help="""The index of the first OCR record to process.""",
    )

    arg_parser.add_argument(
        "--last",
        type=int,
        metavar="INT",
        help="""The index of the last OCR record to process.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
