#!/usr/bin/env python3

import argparse
import base64
import contextlib
import csv
import logging
import os
import textwrap
from datetime import datetime
from pathlib import Path

import openai
import pandas as pd
from openai.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam
)
from tqdm import tqdm

from llama.pylib import io_util, log

SYSTEM_ROLE = textwrap.dedent("""
    You are given an image of a museum specimen with labels.
    I want you to extract all of the text from every label and stamp on the specimen.
    This includes text from both typewritten and handwritten labels.
    It also includes text from stamps and smaller labels.
      ✅ I want ALL of the text.
      ✅ I only want UTF-8 text without markup.
      ❌ DO NOT include HTML tags.
      ❌ DO NOT include markdown tags.
      ❌ DO NOT get confused by the specimen itself which is in the center of the image.
      ❌ Do not hallucinate!
    """)


def ocr_images(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    job_began = datetime.now()

    already_read = get_docs_read(args.doc_csv)

    image_paths = sorted(args.image_dir.glob("*.jpg"))
    image_paths = image_paths[: args.limit]

    client = openai.OpenAI(
        base_url=args.api_host,
        api_key=os.environ.get("OPENAI_API_KEY", "lm-studio"),
    )

    with args.doc_csv.open("a") as tsv:
        writer = csv.writer(tsv)

        if not already_read:
            writer.writerow(["source", "elapsed", "text"])

        sys_role = ChatCompletionSystemMessageParam(role="system", content=SYSTEM_ROLE)

        for image_path in tqdm(image_paths):
            if image_path in already_read:
                continue

            rec_began = datetime.now()

            try:
                with image_path.open("rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")

                response = client.chat.completions.create(
                    model=args.model,
                    messages=[
                        sys_role,
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}",
                                    },
                                },
                            ],
                        }
                    ],
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                )

                text = response.choices[0].message.content

            except openai.APIError:
                logging.exception("API error:")
                continue

            elapsed = str(datetime.now() - rec_began)
            writer.writerow([str(image_path), elapsed, text])
            tsv.flush()

    job_elapsed = str(datetime.now() - job_began)
    msg = f"Job elapsed {job_elapsed}"
    logging.info(msg)

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
        "--model",
        default="chandra-ocr",
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
        help="""Model's context length. Combined input and output.""",
    )
    arg_parser.add_argument(
        "--max-tokens",
        type=int,
        help="""The responses maximum tokens.""",
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
