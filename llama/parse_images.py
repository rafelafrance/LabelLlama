#!/usr/bin/env python3

import argparse
import csv
import json
import logging
import os
import textwrap
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from json.decoder import JSONDecodeError
from pathlib import Path

import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException
from tqdm import tqdm

from llama.model_utils.model_args import ExtractArgs
from llama.model_utils.model_status import ModelStatus, StatusCounts
from llama.model_utils.ocr_docs import OcrDocs
from llama.model_utils.parser_prompt import ParserPrompt
from llama.model_utils.task_writer import TaskWriter
from llama.model_utils.thread_sessions import ThreadSessions
from llama.pylib import image_util, log

TRANSIENT_HTTP_STATUS = {429, 500, 502, 503, 504}


def parse_images(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    prompt = ParserPrompt.load(args.prompt)

    docs = OcrDocs.build(args.image_dir, args.image_glob, args.parsed_file, args.limit)

    if args.input_file:
        docs.tasks += [
            s
            for s in image_util.read_sources(args.input_file)
            if str(s) not in docs.already_done
        ]

    logging.info(f"There are {docs.input_len} images to process")
    logging.info(f"{len(docs.already_done)} images were already done.")
    if docs.limit:
        logging.info(f"Limited to {docs.limit} images.")
    logging.info(f"There are {len(docs.tasks)} images left to process.")

    statuses = StatusCounts()

    extract_args = ExtractArgs(
        prompt=prompt,
        model_id=args.model_id,
        api_host=args.api_host,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        threads=args.threads,
        retries=args.retries,
        retry_backoff=args.retry_backoff,
    )

    with args.parsed_file.open(docs.file_mode) as output_file:
        writer = csv.DictWriter(output_file, prompt.columns)
        if docs.file_mode == "w":
            writer.writeheader()

        with (
            tqdm(total=len(docs.tasks)) as pbar,
            ThreadPoolExecutor(max_workers=args.threads) as executor,
        ):
            sessions = ThreadSessions()
            task_writer = TaskWriter(
                writer=writer,
                out_file=output_file,
                statuses=statuses,
                progress_bar=pbar,
            )
            futures = {
                executor.submit(call_model, extract_args, source, sessions): source
                for source in docs.tasks
            }
            try:
                for future in as_completed(futures):
                    task_writer.write(future, source=futures[future])
            finally:
                sessions.close_all()

    logging.info(
        f"Total {len(docs.tasks)} images processed "
        f"with {statuses.get(ModelStatus.ERROR)} errors "
        f"and {len(docs.already_done)} images skipped."
    )
    log.job_elapsed(job_began)


def call_model(args: ExtractArgs, source: Path | str, sessions: ThreadSessions) -> dict:
    began = datetime.now()

    try:
        base64_image, mime_type = image_util.load_image(source, args.timeout)

        payload = {
            "model": args.model_id,
            "messages": [
                {"role": "system", "content": args.prompt.system_msg},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}",
                            },
                        },
                    ],
                },
            ],
            "response_format": args.prompt.json_schema,
        }
        if args.temperature is not None:
            payload["temperature"] = args.temperature
        if args.max_tokens is not None:
            payload["max_tokens"] = args.max_tokens

        result = post_with_retries(args, payload, sessions.get())

        content = result["choices"][0]["message"]["content"] or ""
        text = content
        extracted = parse_model_json(content)

        status = ModelStatus.SUCCESS

    except (
        IndexError,
        JSONDecodeError,
        KeyError,
        OSError,
        RequestException,
        TypeError,
        ValueError,
    ) as err:
        logging.exception(f"Extract error for: {source}")
        text = str(err)
        status = ModelStatus.ERROR
        extracted = {}

    result = {
        "status": status,
        "source": str(source),
        "elapsed": str(log.task_elapsed(began)),
        "text": text,
    } | extracted

    return result


def parse_model_json(content: str) -> dict:
    extracted = json.loads(content)
    if not isinstance(extracted, dict):
        raise TypeError("Model response JSON must be an object")
    return extracted


def post_with_retries(
    args: ExtractArgs,
    payload: dict,
    session: requests.Session,
) -> dict:
    url = f"{args.api_host}/chat/completions"
    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("LLM_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    last_err: Exception | None = None
    for attempt in range(args.retries + 1):
        try:
            response = session.post(
                url, headers=headers, json=payload, timeout=args.timeout
            )
            if response.status_code in TRANSIENT_HTTP_STATUS and attempt < args.retries:
                sleep_before_retry(args, attempt, response=response)
                continue
            response.raise_for_status()
            return response.json()
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as err:
            last_err = err
            if attempt >= args.retries:
                raise
            sleep_before_retry(args, attempt, err=err)

    if last_err:
        raise last_err
    raise RuntimeError("Extract request failed without a response")


def sleep_before_retry(
    args: ExtractArgs,
    attempt: int,
    response: requests.Response | None = None,
    err: Exception | None = None,
) -> None:
    delay = args.retry_backoff * (2**attempt)
    reason = f"HTTP {response.status_code}" if response is not None else str(err)
    logging.warning(
        "Retrying extract request after %s in %.1f seconds (%s/%s)",
        reason,
        delay,
        attempt + 1,
        args.retries,
    )
    time.sleep(delay)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Use a language model (LM) to extract information directly from
                images, in a single step."""
        ),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--image-dir",
        type=Path,
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
        "--input-file",
        type=Path,
        metavar="path",
        help="""Read a list of image sources (local paths and/or http(s) URLs)
            from this file, one source per line. Blank lines and lines starting
            with '#' are ignored. Can be combined with --image-dir /
            --image-glob, or used on its own.""",
    )
    io_group.add_argument(
        "--parsed-file",
        type=Path,
        required=True,
        metavar="path",
        help="""Write the LM results to this CSV file.
            This appends data to the file.""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt",
        type=Path,
        required=True,
        metavar="path",
        help="""A markdown file with a prompt and list of fields to parse.
            For example prompts/diode_one_v1.md.""",
    )
    model_group = arg_parser.add_argument_group("model options")
    model_defaults = ExtractArgs(ParserPrompt())
    model_group.add_argument(
        "--model-id",
        default=model_defaults.model_id,
        metavar="string",
        help="""Use this language model. (default: %(default)s) There is a speed vs.
            cost trade off between local and hosted models. Local models are cheaper
            but hosted models are much faster. The model must support images.""",
    )
    model_group.add_argument(
        "--api-host",
        default=model_defaults.api_host,
        metavar="string",
        help="""URL for the LM model. (default: %(default)s)
            The default is for LM-Studio, but I also use ChatGPT-nano and other
            server models.""",
    )
    model_group.add_argument(
        "--threads",
        type=int,
        default=model_defaults.threads,
        metavar="int",
        help="""How many parallel threads to run. (default: %(default)s) For
            ChatGPT-nano I will increase this to 20 or more, and for a local model
            I will reduce this to 4 or less.""",
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
        help="""The model's response maximum tokens.
            I use this to truncate model loops.""",
    )
    model_group.add_argument(
        "--timeout",
        type=int,
        default=model_defaults.timeout,
        metavar="int",
        help="""How long to wait for the LM to respond in seconds.
            (default: %(default)s) 5 minutes is a life time for extracting data
            from an image.""",
    )
    model_group.add_argument(
        "--retries",
        type=int,
        default=model_defaults.retries,
        metavar="int",
        help="""Retry transient extract request failures this many times.
            (default: %(default)s)""",
    )
    model_group.add_argument(
        "--retry-backoff",
        type=float,
        default=model_defaults.retry_backoff,
        metavar="float",
        help="""Initial seconds to wait before retrying transient extract request
            failures. The delay doubles after each failed attempt.
            (default: %(default)s)""",
    )
    logging_group = arg_parser.add_argument_group("logging options")
    logging_group.add_argument(
        "--log-file",
        type=Path,
        metavar="path",
        help="""Append logging notices to this file. It also logs the script arguments
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
        help="""Limit to this many images.""",
    )
    ns = arg_parser.parse_args(args)
    if not ns.image_dir and not ns.image_glob and not ns.input_file:
        arg_parser.error(
            "one of --image-dir, --image-glob, or --input-file is required"
        )
    if ns.image_dir and not ns.image_dir.is_dir():
        arg_parser.error(f"--image-dir is not a directory: {ns.image_dir}")
    if not ns.prompt.is_file():
        arg_parser.error(f"--prompt is not a file: {ns.prompt}")
    if ns.threads < 1:
        arg_parser.error("--threads must be >= 1")
    if ns.timeout < 1:
        arg_parser.error("--timeout must be >= 1")
    if ns.max_tokens is not None and ns.max_tokens < 1:
        arg_parser.error("--max-tokens must be >= 1")
    if ns.limit is not None and ns.limit < 1:
        arg_parser.error("--limit must be >= 1")
    if ns.retries < 0:
        arg_parser.error("--retries must be >= 0")
    if ns.retry_backoff < 0:
        arg_parser.error("--retry-backoff must be >= 0")
    return ns


if __name__ == "__main__":
    load_dotenv()
    ARGS = parse_args()
    parse_images(ARGS)
