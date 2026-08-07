#!/usr/bin/env python3

import argparse
import csv
import logging
import os
import textwrap
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from tqdm import tqdm

from llama.pylib import fix_ocr, log
from llama.pylib.parser_util import (
    FIRST_COLUMNS,
    ParsedDocs,
    ParserArgs,
    ParserCleaner,
    ParserPrompt,
)

if TYPE_CHECKING:
    from llama.pylib.ocr_util import OcrResult

MIN_SIZE = 1024
DEFAULT_POOL = 10


def parse_text(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    parsed_docs = ParsedDocs.build(args.parsed_file, args.ocr_file, args.limit)

    logging.info(f"There are {len(parsed_docs.ocr_records)} documents to parse.")
    logging.info(f"{len(parsed_docs.already_parsed)} documents were already parsed.")
    if parsed_docs.limit:
        logging.info(f"Limited to {parsed_docs.limit} images.")
    logging.info(f"There are {len(parsed_docs.tasks)} docs left to parse.")

    prompt = ParserPrompt.load(args.prompt)
    prompt.log_size()

    statuses = defaultdict(int)

    parser_args = ParserArgs(
        prompt=prompt,
        model_name=args.model_name,
        api_host=args.api_host,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        threads=args.threads,
    )

    with args.parse_file.open(parsed_docs.parsed_file_mode) as parse_file:
        writer = csv.DictWriter(parse_file, FIRST_COLUMNS + prompt.column_names)
        if parsed_docs.parsed_file_mode == "w":
            writer.writeheader()

        with (
            tqdm(total=len(parsed_docs.tasks)) as pbar,
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
                executor.submit(parser, parser_args, ocr_result, session)
                for ocr_result in parsed_docs.tasks
            }
            for future in as_completed(futures):
                result = future.result()
                statuses[result["status"]] += 1
                writer.writerow(result)
                pbar.update(1)
                parse_file.flush()

    logging.info(
        f"Total {len(parsed_docs.tasks)} documents processed "
        f"with {statuses['ERROR']} errors "
        f"and {len(parsed_docs.already_parsed)} documents were skipped."
    )

    log.job_elapsed(job_began)


def parser(
    args: ParserArgs,
    ocr_result: OcrResult,
    session: requests.Session,
) -> dict:
    began = datetime.now()

    text = fix_ocr.prepare_for_parse(ocr_result.text)

    url = f"{args.api_host}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('LLM_API_KEY')}",
    }
    payload = {
        "model": args.model_name,
        "messages": [
            {"role": "system", "content": args.prompt.system_prompt},
            {"role": "user", "content": args.prompt.build_text_prompt(text)},
        ],
    }
    if args.temperature is not None:
        payload["temperature"] = args.temperature
    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens

    extracted = {}
    try:
        response = session.post(
            url, headers=headers, json=payload, timeout=args.timeout
        )
        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"] or ""
        extracted = ParserCleaner.llm_reply_to_dict(content, args.prompt.column_names)
        status = "success"

    except requests.exceptions.RequestException as err:
        logging.exception(f"Parse error for: {Path(ocr_result.source).name}")
        text = str(err)
        status = "ERROR"

    result = {
        "status": status,
        "source": ocr_result.source,
        "elapsed": str(log.task_elapsed(began)),
        "text": text,
    } | extracted

    return result


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Use a language model (LM) to extract information from text."""
        ),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--ocr-file",
        type=Path,
        metavar="path",
        help="""Parse label text from this file. We need only 'source' and 'text'
            columns for valid input, so any CSV file with those columns is fine.""",
    )
    io_group.add_argument(
        "--parse-file",
        type=Path,
        metavar="path",
        help="""Write the LM results to this CSV file.""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt",
        type=Path,
        required=True,
        metavar="path",
        help="""A markdown file with a prompt and list of fields to parse.
            For example prompts/fields/herbarium_v1.md.""",
    )
    model_group = arg_parser.add_argument_group("model options")
    model_group.add_argument(
        "--model-name",
        default="lm_studio/google/gemma-4-26b-a4b",
        metavar="string",
        help="""Use this language model. (default: %(default)s) There is a speed vs.
            cost trade off between local and hosted models. Local models are cheaper
            but hosted models are much faster.""",
    )
    model_group.add_argument(
        "--api-host",
        default="http://localhost:1234/v1",
        metavar="string",
        help="""URL for the LM model. (default %(default)s
            The default is for LM-Studio, but I also use ChatGPT-nano and other
            server models.""",
    )
    model_group.add_argument(
        "--threads",
        type=int,
        default=10,
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
        help="""The OCR model's response maximum tokens.
            I use this to truncate model loops.""",
    )
    model_group.add_argument(
        "--timeout",
        type=int,
        default=120,
        metavar="int",
        help="""How long to wait for the LM to respond in seconds.
            (default: %(default)s) 2 minutes is a life time for parsing label text.""",
    )
    logging_group = arg_parser.add_argument_group("logging options")
    logging_group.add_argument(
        "--log-file",
        type=Path,
        metavar="string",
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
        help="""Limit to this many records.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    load_dotenv()
    ARGS = parse_args()
    parse_text(ARGS)
