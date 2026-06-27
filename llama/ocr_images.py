#!/usr/bin/env python3

import argparse
import base64
import csv
import logging
import textwrap
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm

from llama.pylib import io_util, prompt_util, str_util, timer

MIN_SIZE = 1024

COLUMN_NAMES = ["status", "source", "text", "elapsed"]

DEFAULT_POOL = 10


def ocr_images(args: argparse.Namespace) -> None:
    job_began = timer.job_began(args.log_file, args=args)

    mode = "w"  # Used as a flag for writing the header elsewise "a" would work
    already_read = set()
    if args.ocr_file.exists() and args.ocr_file.stat().st_size >= MIN_SIZE:
        mode = "a"
        records = io_util.read_list_of_dicts(args.ocr_file)
        already_read = {
            r["source"]
            for r in records
            if r.get("source") and r.get("status") == "success"
        }

    image_paths = sorted(Path().glob(args.image_glob))
    image_paths = image_paths[: args.limit]
    logging.info(f"There are {len(image_paths)} images to OCR")
    logging.info(f"{len(already_read)} images were already read.")

    prompt = prompt_util.Prompt.load(args.prompt)
    prompt.log_size()

    tasks = [path for path in image_paths if str(path) not in already_read]

    statuses = defaultdict(int)

    with args.ocr_file.open(mode) as ocr_file:
        writer = csv.DictWriter(ocr_file, COLUMN_NAMES)
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

            futures = {
                executor.submit(
                    call_ocr, args, image_path, prompt.system_prompt, session
                ): image_path
                for image_path in tasks
            }

            for future in as_completed(futures):
                result = future.result()
                statuses[result["status"]] += 1
                writer.writerow(result)
                pbar.update(1)

    logging.info(
        f"Total {len(image_paths)} documents processed with {statuses['ERROR']} errors "
        f"and {len(already_read)} documents were skipped."
    )

    timer.job_elapsed(job_began)


def call_ocr(
    args: argparse.Namespace,
    image_path: Path,
    sys_prompt: str,
    session: requests.Session,
) -> dict:
    began = datetime.now()

    with image_path.open("rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")

    url = f"{args.api_host}/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            },
        ],
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }

    try:
        response = session.post(
            url, headers=headers, json=payload, timeout=args.timeout
        )
        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"] or ""

        if args.convert_html:
            text = str_util.html_to_text(content)
        else:
            text = str_util.clean_ocr(content)
        status = "success"

    except requests.exceptions.RequestException as err:
        logging.exception(f"API error for: {image_path.name}")
        text = str(err)
        status = "ERROR"

    result = {
        "status": status,
        "source": str(image_path),
        "text": text,
        "elapsed": str(timer.task_elapsed(began)),
    }

    return result


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""OCR images."""),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--image-glob",
        required=True,
        metavar="glob",
        help="""Get all images matching this glob/pattern. You may need to quote this
            argument. An example: 'museum/data/images1/*.jpg'""",
    )
    io_group.add_argument(
        "--ocr-file",
        type=Path,
        required=True,
        metavar="path",
        help="""Put OCRed text into this file. This appends data to the file.
            An example: data/museum/data/images1.csv""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt",
        type=Path,
        default="prompts/ocr_v2.md",
        metavar="path",
        help="""A markdown file with a prompt used to OCR images.
            (default: %(default)s)""",
    )
    model_group = arg_parser.add_argument_group("model options")
    model_group.add_argument(
        "--model",
        default="chandra-ocr",
        metavar="string",
        help="""Use this language model. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--api-host",
        default="http://localhost:1234/v1",
        metavar="string",
        help="""URL for the language model. (default: %(default)s)
            The default is for LM-Studio, but you could use Ollama's or another
            URL here.""",
    )
    model_group.add_argument(
        "--threads",
        type=int,
        default=2,
        metavar="int",
        help="""How many parallel threads to run. (default: %(default)s)
            Increase this if the model server is powerful enough.""",
    )
    model_group.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        metavar="float",
        help="""Model's temperature. (default: %(default)s)
            We don't want the model to get creative, so keep this value low.""",
    )
    model_group.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        metavar="int",
        help="""The OCR model's response maximum tokens. (default: %(default)s)
            2048 tokens is roughly 1.5K words, which is more than enough for most
            museum specimens. I keep this low to truncate model loops.""",
    )
    model_group.add_argument(
        "--timeout",
        type=int,
        default=120,
        metavar="int",
        help="""How long to wait for the OCR model to complete in seconds.
            (default: %(default)s) 2 minutes is a life time for OCR.""",
    )
    model_group.add_argument(
        "--convert-html",
        action="store_true",
        help="""A flag. If the OCR model insists on producting HTML output, you may want
            to convert it to text. Use this flag to trigger the conversion.""",
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
        help="""Only OCR this many images.""",
    )
    ns: argparse.Namespace = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    ocr_images(ARGS)
