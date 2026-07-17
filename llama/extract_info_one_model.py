#!/usr/bin/env python3

"""Extract text information from images of museum specimens using one model."""

import argparse
import base64
import csv
import logging
import re
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm

from llama.pylib import image_util, log, prompt_util

FIRST_COLUMNS = ["status", "source", "elapsed"]
MIN_SIZE = 1024
DEFAULT_POOL = 10


def extract(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    mode = "w"  # Used as a flag for writing the header elsewise "a" would work fine
    already_done = set()
    if args.extractions.exists() and args.extractions.stat().st_size >= MIN_SIZE:
        mode = "a"
        records = pd.read_csv(args.extractions, dtype=str).fillna("").to_dict("records")
        already_done = {
            r["source"]
            for r in records
            if r.get("source") and r.get("status") == "success"
        }

    image_paths = image_util.get_images(args.image_dir, args.limit)

    total, done = len(image_paths), len(already_done)
    logging.info(f"There are {total} images to process")
    logging.info(f"{done} images were already done.")
    logging.info(f"There are {total - done} images left to process.")

    prompt = prompt_util.Prompt.load(args.prompt)
    prompt.log_size()

    tasks = [path for path in image_paths if str(path) not in already_done]

    statuses = {"success": 0, "error": 0, "blank": 0}

    with args.extractions.open(mode) as extract:
        writer = csv.DictWriter(extract, fieldnames=FIRST_COLUMNS + prompt.column_names)
        if mode == "w":
            writer.writeheader()

        with (
            tqdm(total=len(tasks)) as pbar,
            ThreadPoolExecutor(max_workers=args.threads) as executor,
            requests.Session() as session,
        ):
            if args.threads > DEFAULT_POOL:
                adapter = HTTPAdapter(
                    pool_connections=args.threads, pool_maxsize=args.threads
                )
                session.mount("http://", adapter)
                session.mount("https://", adapter)

            futures = [
                executor.submit(send_to_llm, args, image_path, prompt, session)
                for image_path in tasks
            ]

            for future in as_completed(futures):
                result = future.result()
                status = "error"
                if result["status"] in ("success", "empty"):
                    status = result["status"]
                statuses[status] += 1
                writer.writerow(result)
                pbar.update(1)
                extract.flush()

    logging.info(
        f"Total {len(image_paths)} documents processed with {statuses['error']} errors "
        f"and {len(already_done)} documents were already done."
    )
    log.job_elapsed(job_began)


def send_to_llm(
    args: argparse.Namespace,
    image_path: Path,
    prompt: prompt_util.Prompt,
    session: requests.Session,
) -> dict:
    began = datetime.now()

    with image_path.open("rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")

    url = f"{args.api_host}/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "messages": [
            {"role": "system", "content": prompt.system_prompt},
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
    if args.model:
        payload["model"] = args.model

    extracted = {}
    try:
        response = session.post(
            url, headers=headers, json=payload, timeout=args.timeout
        )
        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"] or ""

        extracted = llm_reply_to_dict(content, prompt)
        extracted = clean_reply(extracted, prompt)

        status = "success"

    except requests.exceptions.RequestException as err:
        logging.exception(f"Extraction error for: {image_path.name}")
        status = str(err)

    result = {
        "status": status,
        "source": str(image_path),
        "elapsed": str(log.task_elapsed(began)),
    } | extracted

    return result


def llm_reply_to_dict(content: str, prompt: prompt_util.Prompt) -> dict:
    """Convert an LM reply in prompt_util.get_field_template format to a dict."""
    # Get field names and the values
    splits = re.split(r"^<< ## (\w+) ## >>$", content, flags=re.MULTILINE)

    # Remove first blank split
    if splits[0].strip() == "":
        splits = splits[1:]

    # Try to match field names with values
    as_dict = {
        k: v.strip()
        for k, v in zip(splits[::2], splits[1::2], strict=False)
        if k in prompt.column_names
    }

    return as_dict


def clean_reply(in_row: dict, prompt: prompt_util.Prompt) -> dict:
    out_row = {}

    for column in prompt.column_names:
        field_action = prompt.field_classes[column]

        in_data = {k: in_row.get(k) for k in field_action.get_field_names()}

        out_field = field_action(**in_data)
        out_field.cross_field_update(in_row)

        cell = getattr(out_field, column)
        cell = "" if cell == column else cell  # Stop echo where llm sets value to label
        out_row[column] = cell

    return out_row


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Extract information from images of museum specimens."""
        ),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        metavar="path",
        help="""Extract information from all images in this directory.""",
    )
    io_group.add_argument(
        "--extractions",
        type=Path,
        required=True,
        metavar="path",
        help="""Put extracted data into this CSV file.
            This appends data to the file.""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt",
        type=Path,
        default="prompts/extraction.md",
        metavar="path",
        help="""A markdown file with a prompt used to extract the data.
            (default: %(default)s)""",
    )
    model_group = arg_parser.add_argument_group("model options")
    model_group.add_argument(
        "--model",
        default="chandra-ocr",
        metavar="model",
        help="""Use this language model. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--api-host",
        default="http://localhost:8080/v1",
        metavar="url",
        help="""URL for the language model. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--threads",
        type=int,
        default=2,
        metavar="int",
        help="""How many parallel threads to run. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--timeout",
        type=int,
        default=120,
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
