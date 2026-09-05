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

from llama.model_utils.task_writer import TaskWriter
from llama.model_utils.model_args import ParserArgs
from llama.model_utils.model_status import ModelStatus, StatusCounts
from llama.model_utils.parsed_docs import ParsedDocs
from llama.model_utils.parser_prompt import ParserPrompt
from llama.model_utils.thread_sessions import ThreadSessions
from llama.pylib import fix_ocr, log

TRANSIENT_HTTP_STATUS = {429, 500, 502, 503, 504}


def parse_text(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    prompt = ParserPrompt.load(args.prompt)

    docs = ParsedDocs.build(
        args.parsed_file,
        args.ocr_file,
        args.limit,
        expected_columns=prompt.columns,
    )

    logging.info(f"There are {docs.input_len} documents to process")
    logging.info(f"{len(docs.already_done)} documents were already done.")
    if docs.limit:
        logging.info(f"Limited to {docs.limit} documents.")
    logging.info(f"There are {len(docs.tasks)} documents left to process.")

    statuses = StatusCounts()

    parser_args = ParserArgs(
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
                executor.submit(
                    call_model, parser_args, ocr_result, sessions
                ): ocr_result
                for ocr_result in docs.tasks
            }
            try:
                for future in as_completed(futures):
                    task_writer.write(future, source=futures[future]["source"])
            finally:
                sessions.close_all()

    logging.info(
        f"Total {len(docs.tasks)} documents processed "
        f"with {statuses.get(ModelStatus.ERROR)} errors "
        f"and {len(docs.already_done)} documents skipped."
    )
    log.job_elapsed(job_began)


def call_model(
    args: ParserArgs,
    ocr_result: dict,
    sessions: ThreadSessions,
) -> dict:
    began = datetime.now()

    text = fix_ocr.prepare_for_parse(ocr_result["text"])

    payload = {
        "model": args.model_id,
        "messages": [
            {"role": "system", "content": args.prompt.system_msg},
            {"role": "user", "content": args.prompt.build_text_msg(text)},
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
        result = post_with_retries(args, payload, sessions.get())

        content = result["choices"][0]["message"]["content"] or ""
        extracted = parse_model_json(content)

        status = ModelStatus.SUCCESS

    except (
        RequestException,
        JSONDecodeError,
        ValueError,
        KeyError,
        IndexError,
        TypeError,
    ) as err:
        logging.exception(f"Parse error for: {Path(ocr_result['source']).name}")
        text = str(err)
        status = ModelStatus.ERROR

    result = {
        "status": status,
        "source": ocr_result["source"],
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
    args: ParserArgs,
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
    raise RuntimeError("Parse request failed without a response")


def sleep_before_retry(
    args: ParserArgs,
    attempt: int,
    response: requests.Response | None = None,
    err: Exception | None = None,
) -> None:
    delay = args.retry_backoff * (2**attempt)
    reason = f"HTTP {response.status_code}" if response is not None else str(err)
    logging.warning(
        "Retrying parse request after %s in %.1f seconds (%s/%s)",
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
            """Use a language model (LM) to extract information from text."""
        ),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--ocr-file",
        type=Path,
        required=True,
        metavar="path",
        help="""Parse label text from this file. We need only 'source' and 'text'
            columns for valid input, so any CSV file with those columns is fine.""",
    )
    io_group.add_argument(
        "--parsed-file",
        type=Path,
        required=True,
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
            For example prompts/llm_fields/herbarium_v1.md.""",
    )
    model_group = arg_parser.add_argument_group("model options")
    model_defaults = ParserArgs(ParserPrompt())
    model_group.add_argument(
        "--model-id",
        default=model_defaults.model_id,
        metavar="string",
        help="""Use this language model. (default: %(default)s) There is a speed vs.
            cost trade off between local and hosted models. Local models are cheaper
            but hosted models are much faster.""",
    )
    model_group.add_argument(
        "--api-host",
        default=model_defaults.api_host,
        metavar="string",
        help="""URL for the LM model. (default %(default)s
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
        help="""The OCR model's response maximum tokens.
            I use this to truncate model loops.""",
    )
    model_group.add_argument(
        "--timeout",
        type=int,
        default=model_defaults.timeout,
        metavar="int",
        help="""How long to wait for the LM to respond in seconds.
            (default: %(default)s) 2 minutes is a life time for parsing label text.""",
    )
    model_group.add_argument(
        "--retries",
        type=int,
        default=model_defaults.retries,
        metavar="int",
        help="""Retry transient parse request failures this many times.
            (default: %(default)s)""",
    )
    model_group.add_argument(
        "--retry-backoff",
        type=float,
        default=model_defaults.retry_backoff,
        metavar="float",
        help="""Initial seconds to wait before retrying transient parse request
            failures. The delay doubles after each failed attempt.
            (default: %(default)s)""",
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
    if not ns.ocr_file.is_file():
        arg_parser.error(f"--ocr-file is not a file: {ns.ocr_file}")
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
    parse_text(ARGS)
