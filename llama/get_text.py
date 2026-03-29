#!/usr/bin/env python3

import argparse
import csv
import logging
import textwrap
from datetime import datetime
from pathlib import Path

import lmstudio as lms
from tqdm import tqdm

from llama.common import log

# A reasonable starting prompt. I will parameterize and try variations on this later.
PROMPT_V1 = " ".join(
    """
    You are given an image of a museum specimen with labels.
    I want you to extract all of the text from every label on the specimen.
    This includes text from both typewritten and handwritten labels.
    Do not get confused by the specimen itself which is in the center of the image.
    I want plain text without HTML tags, HTML entities, MATHML tags, or markdown tags.
    Do not hallucinate.
    """.split(),
)


def ocr_images(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    field_names = ["source", "text", "elapsed"]
    mode = "w"
    done = []

    if args.doc_tsv.exists():
        mode = "a"
        with args.doc_tsv.open() as tsv:
            reader = csv.DictReader(tsv, delimiter="\t")
            done = [r["source"] for r in reader]

    image_paths = sorted(args.image_dir.glob("*.jpg"))

    with lms.Client(args.api_host) as client, args.doc_tsv.open(mode) as tsv:
        writer = csv.DictWriter(tsv, fieldnames=field_names, delimiter="\t")

        config = lms.LlmLoadModelConfigDict(contextLength=args.context_length)
        model = client.llm.model(args.model_name, config=config)

        for image_path in tqdm(image_paths):
            if image_path in done:
                continue

            rec_began = datetime.now()

            handle = client.files.prepare_image(image_path)
            chat = lms.Chat()
            chat.add_user_message(PROMPT_V1, images=[handle])

            try:
                config = lms.LlmPredictionConfigDict(
                    temperature=args.temperature,
                    maxTokens=args.max_tokens,
                )
                text = model.respond(chat, config=config)
            except lms.LMStudioServerError:
                logging.exception("Server error:")
                continue

            elapsed = str(datetime.now() - rec_began)
            writer.writerow(
                {"source": str(image_path), "text": text, "elapsed": elapsed},
            )

    log.finished()


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
        "--doc-tsv",
        type=Path,
        required=True,
        help="""Put OCRed text into this TSV file.
            This appends data to the file.""",
    )
    arg_parser.add_argument(
        "--model",
        default="noctrex/Chandra-OCR-GGUF/Chandra-OCR-Q4_K_S.gguf",
        help="""Use this language model. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--api-host",
        default="http://localhost:1234",
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
    ns: argparse.Namespace = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    ocr_images(ARGS)
