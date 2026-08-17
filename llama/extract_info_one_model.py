#!/usr/bin/env python3

"""Extract text information from images of museum specimens using a single model."""

import argparse
import base64
import csv
import json
import logging
import textwrap
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm

from llama.model_utils.model_args import ExtractArgs
from llama.model_utils.model_prompts import ParserPrompt
from llama.model_utils.model_status import ModelStatus
from llama.model_utils.ocr_docs import OcrDocs
from llama.pylib import log

FIRST_COLUMNS = ["status", "source", "elapsed"]
MIN_SIZE = 1024
DEFAULT_POOL = 10


def extract(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    docs = OcrDocs.build(args.image_dir, args.image_glob, args.ocr_file, args.limit)

    logging.info(f"There are {len(docs.image_paths)} images to process")
    logging.info(f"{len(docs.ocr_success)} images were already done.")
    if docs.limit:
        logging.info(f"Limited to {docs.limit} images.")
    logging.info(f"There are {len(docs.tasks)} images left to process.")

    prompt = ParserPrompt.load(args.prompt)

    statuses = defaultdict(int)

    model_args = ExtractArgs(
        prompt=prompt,
        api_host=args.api_host,
        model_id=args.model_id,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        threads=args.threads,
    )

    with args.extractions.open(docs.file_mode) as parsed_file:
        writer = csv.DictWriter(parsed_file, FIRST_COLUMNS + prompt.column_names)
        if docs.file_mode == "w":
            writer.writeheader()

        with (
            tqdm(total=len(docs.tasks)) as pbar,
            ThreadPoolExecutor(max_workers=args.threads) as executor,
            requests.Session() as session,
        ):
            if args.threads > DEFAULT_POOL:
                adapter = HTTPAdapter(
                    pool_connections=args.threads, pool_maxsize=args.threads
                )
                session.mount("http://", adapter)
                session.mount("https://", adapter)

            futures = {
                executor.submit(parser, model_args, image_path, prompt, session)
                for image_path in docs.tasks
            }
            for future in as_completed(futures):
                pbar.update(1)
                result = future.result()
                try:
                    writer.writerow(result)
                    statuses[result["status"]] += 1
                    parsed_file.flush()
                except ValueError as err:
                    logging.exception(f"Parse error for: {Path(result['source']).name}")
                    text = str(err)
                    logging.exception(text)
                    writer.writerow(
                        {
                            "status": ModelStatus.ERROR,
                            "source": result["source"],
                            "text": text,
                        }
                    )

    logging.info(
        f"Total {len(docs.tasks)} documents processed "
        f"with {statuses[ModelStatus.ERROR]} errors "
        f"and {len(docs.ocr_success)} documents skipped."
    )

    log.job_elapsed(job_began)


def parser(
    args: ExtractArgs,
    image_path: Path,
    prompt: ParserPrompt,
    session: requests.Session,
) -> dict:
    began = datetime.now()

    with image_path.open("rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")

    url = f"{args.api_host}/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "messages": [
            {"role": "system", "content": prompt.system_msg},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
    }
    if args.temperature is not None:
        payload["temperature"] = args.temperature
    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens
    if args.prompt.json_schema:
        payload["character_schema"] = args.prompt.json_schema

    extracted = {}
    try:
        response = session.post(
            url, headers=headers, json=payload, timeout=args.timeout
        )
        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"] or ""
        extracted = json.loads(content)

        status = ModelStatus.SUCCESS

    except requests.exceptions.RequestException as err:
        logging.exception(f"Extraction error for: {image_path.name}")
        status = str(err)
        status = ModelStatus.ERROR

    result = {
        "status": status,
        "source": str(image_path),
        "elapsed": str(log.task_elapsed(began)),
    } | extracted

    return result


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
            Extract information from images of museum specimens using a single model.
            """
        ),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Extract information from all images in this directory.""",
    )
    io_group.add_argument(
        "--image-glob",
        metavar="GLOB",
        help="""Get all images matching this glob/pattern. You will need to quote this
            argument. An example: 'museum/data/images1/*.jpg'""",
    )
    io_group.add_argument(
        "--extractions",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Put extracted data into this CSV file.
            This appends data to the file.""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt",
        type=Path,
        metavar="PATH",
        help="""A markdown file with a prompt used to extract the data.
            (default: %(default)s)""",
    )
    model_group = arg_parser.add_argument_group("model options")
    model_defaults = ExtractArgs(ParserPrompt())
    model_group.add_argument(
        "--model-id",
        default=model_defaults.model_id,
        metavar="STRING",
        help="""Use this language model. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--api-host",
        default=model_defaults.api_host,
        metavar="url",
        help="""URL for the language model. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--threads",
        type=int,
        default=model_defaults.threads,
        metavar="int",
        help="""How many parallel threads to run. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--temperature",
        type=float,
        metavar="float",
        help="""Model's temperature.
            We don't want the model to get creative, so keep this value low. Some
            hosted servers don't like this option so there is no default.""",
    )
    model_group.add_argument(
        "--max-tokens",
        type=int,
        metavar="int",
        help="""The OCR model's response maximum tokens.
            I use this to truncate model loops.""",
    )
    model_group.add_argument(
        "--timeout",
        type=int,
        default=model_defaults.timeout,
        metavar="int",
        help="""How long to wait for the OCR model to complete in seconds.
            (default: %(default)s).""",
    )
    logging_group = arg_parser.add_argument_group("logging options")
    logging_group.add_argument(
        "--log-file",
        type=Path,
        metavar="path",
        help="""Append logging notices to this file. It also logs the script options
            so you may use this to keep track of what you did.""",
    )
    logging_group.add_argument(
        "--notes",
        metavar="string",
        help="""Notes for logging. They only appear in the log file.""",
    )
    debugging_group = arg_parser.add_argument_group("debugging options")
    debugging_group.add_argument(
        "--limit",
        type=int,
        metavar="int",
        help="""Only extract data from this many images.""",
    )
    ns: argparse.Namespace = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    extract(ARGS)
