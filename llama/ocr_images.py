#!/usr/bin/env python3

import argparse
import base64
import csv
import logging
import textwrap
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm

from llama.pylib import fix_ocr, log, prompt_util
from llama.pylib.ocr_docs import OcrDocs, OcrModelArgs, OcrResult, OcrStatus

DEFAULT_POOL = 10


def ocr_images(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    ocr_docs = OcrDocs.ocr_docs(
        args.image_dir, args.image_glob, args.ocr_file, args.limit
    )
    tasks = ocr_docs.to_do()

    logging.info(f"There are {ocr_docs.total} images to OCR")
    logging.info(f"{ocr_docs.previously_done} images were already done.")
    logging.info(f"There are {ocr_docs.remaining} images left to OCR.")

    prompt = prompt_util.Prompt.load(args.prompt)
    prompt.log_size()

    statuses = defaultdict(int)

    model_args = OcrModelArgs(
        api_host=args.api_host,
        model_name=args.model_name,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        convert_html=args.convert_html,
    )

    with args.ocr_file.open(ocr_docs.ocr_file_mode) as ocr_file:
        writer = csv.DictWriter(ocr_file, ocr_docs.field_names)
        if ocr_docs.ocr_file_mode == "w":
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
                executor.submit(
                    call_ocr, model_args, image_path, prompt.system_prompt, session
                )
                for image_path in tasks
            ]

            for future in as_completed(futures):
                result = future.result()
                statuses[result.status] += 1
                writer.writerow(asdict(result))
                pbar.update(1)
                ocr_file.flush()

    logging.info(
        f"Total {ocr_docs.total} documents processed with {statuses['ERROR']} errors "
        f"and {ocr_docs.previously_done} documents were skipped."
    )

    log.job_elapsed(job_began)


def call_ocr(
    args: OcrModelArgs,
    image_path: Path,
    sys_prompt: str,
    session: requests.Session,
) -> OcrResult:
    began = datetime.now()

    with image_path.open("rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")

    url = f"{args.api_host}/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": args.model_name,
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
            content = fix_ocr.html_to_md(content)

        text = fix_ocr.clean_ocr(content)
        status = OcrStatus.SUCCESS

    except requests.exceptions.RequestException as err:
        logging.exception(f"OCR error for: {image_path.name}")
        text = str(err)
        status = OcrStatus.ERROR

    result = OcrResult(
        status=status,
        source=str(image_path),
        elapsed=str(log.task_elapsed(began)),
        text=text,
    )

    return result


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""OCR images."""),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--image-dir",
        metavar="PATH",
        help="""OCR all images in this directory.""",
    )
    io_group.add_argument(
        "--image-glob",
        metavar="GLOB",
        help="""Get all images matching this glob/pattern. You will need to quote this
            argument. An example: 'museum/data/images1/*.jpg'""",
    )
    io_group.add_argument(
        "--ocr-file",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Put OCRed text into this CSV file. This appends data to the file.""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt",
        type=Path,
        default="prompts/ocr_v2.md",
        metavar="PATH",
        help="""A markdown file with a prompt used to OCR images.
            (default: %(default)s)""",
    )
    model_group = arg_parser.add_argument_group("model options")
    model_defaults = OcrModelArgs()
    model_group.add_argument(
        "--model-name",
        default=model_defaults.model_name,
        metavar="STRING",
        help="""Use this language model. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--api-host",
        default=model_defaults.api_host,
        metavar="STRING",
        help="""URL for the language model. (default: %(default)s)
            The default is for LM-Studio, but you could use Ollama's or another
            URL here.""",
    )
    model_group.add_argument(
        "--threads",
        type=int,
        default=model_defaults.threads,
        metavar="INT",
        help="""How many parallel threads to run. (default: %(default)s)
            Increase this if the model server is powerful enough.""",
    )
    model_group.add_argument(
        "--temperature",
        type=float,
        default=model_defaults.temperature,
        metavar="FLOAT",
        help="""Model's temperature. (default: %(default)s)
            We don't want the model to get creative, so keep this value low.""",
    )
    model_group.add_argument(
        "--max-tokens",
        type=int,
        default=model_defaults.max_tokens,
        metavar="INT",
        help="""The OCR model's response maximum tokens. (default: %(default)s)
            2048 tokens is roughly 1.5K words, which is more than enough for most
            museum specimens. I keep this low to truncate model loops.""",
    )
    model_group.add_argument(
        "--timeout",
        type=int,
        default=model_defaults.timeout,
        metavar="INT",
        help="""How long to wait for the OCR model to complete in seconds.
            (default: %(default)s) 2 minutes is a life time for OCR.""",
    )
    model_group.add_argument(
        "--convert-html",
        action="store_true",
        help="""A flag. If the OCR model insists on producing HTML output, you may want
            to convert it to markdown. Use this flag to trigger the conversion.""",
    )
    logging_group = arg_parser.add_argument_group("logging options")
    logging_group.add_argument(
        "--log-file",
        type=Path,
        metavar="PATH",
        help="""Append logging notices to this file. It also logs the script options
            so you may use this to keep track of what you did.""",
    )
    logging_group.add_argument(
        "--notes",
        metavar="STRING",
        help="""Notes for logging. They only appear in the log file.""",
    )
    debugging_group = arg_parser.add_argument_group("debugging options")
    debugging_group.add_argument(
        "--limit",
        type=int,
        metavar="INT",
        help="""Only OCR this many images.""",
    )
    ns: argparse.Namespace = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    ocr_images(ARGS)
