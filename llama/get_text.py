#!/usr/bin/env python3

import argparse
import contextlib
import csv
import logging
import textwrap
from datetime import datetime
from pathlib import Path

import lmstudio as lms
import pandas as pd
from tqdm import tqdm

from llama.common import io_util, log
from llama.ocr import all_ocr_parameters


def ocr_images(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    already_read = get_docs_read(args.doc_csv)

    ocr_params = all_ocr_parameters.get_parameters(args.model_name)

    image_paths = sorted(args.image_dir.glob("*.jpg"))
    image_paths = image_paths[: args.limit]

    with lms.Client() as client, args.doc_csv.open("a") as tsv:
        writer = csv.writer(tsv)

        if not already_read:
            writer.writerow(["source", "elapsed", "text"])

        model_config = lms.LlmLoadModelConfigDict(contextLength=args.context_length)
        model = client.llm.model(args.model_name, config=model_config)

        response_config = lms.LlmPredictionConfigDict(
            temperature=args.temperature,
            maxTokens=args.max_tokens,
        )

        for image_path in tqdm(image_paths):
            if image_path in already_read:
                continue

            rec_began = datetime.now()

            handle = client.files.prepare_image(image_path)
            chat = lms.Chat()
            chat.add_user_message(ocr_params["prompt"], images=[handle])

            try:
                response = model.respond(chat, config=response_config)
            except lms.LMStudioServerError:
                logging.exception("Server error:")
                continue

            text = ocr_params["cleaner"](str(response))

            elapsed = str(datetime.now() - rec_began)
            writer.writerow([str(image_path), elapsed, text])
            tsv.flush()

    log.finished()


def get_docs_read(doc_csv: Path) -> list[Path]:
    done = []
    if doc_csv.exists():
        with contextlib.suppress(pd.errors.EmptyDataError):
            records = io_util.read_list_of_dicts(doc_csv)
            done = [Path(r["source"]) for r in records if r.get("source")]
    return done


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""OCR images."""),
    )
    arg_parser.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        help="""Directory containing all of the images to OCR.""",
    )
    arg_parser.add_argument(
        "--doc-csv",
        type=Path,
        required=True,
        help="""Put OCRed text into this CSV file. This appends data to the file.""",
    )
    arg_parser.add_argument(
        "--model-name",
        default="chandra-ocr-2",
        help="""Use this language model. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--api-host",
        default="http://localhost:1234/v1",
        help="""URL for the language model. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--context-length",
        type=int,
        help="""Model's context length. Combined input and output.
            (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--max-tokens",
        type=int,
        help="""The responses maximum tokens. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="""Model's temperature. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    arg_parser.add_argument(
        "--notes",
        help="""Notes for logging.""",
    )
    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Only read this many records.""",
    )
    ns: argparse.Namespace = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    ocr_images(ARGS)
