#!/usr/bin/env python3

import argparse
import csv
import json
import logging
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from json.decoder import JSONDecodeError
from pathlib import Path

from dotenv import load_dotenv
from requests.exceptions import RequestException
from tqdm import tqdm

from llama.model_utils.model_status import ModelStatus, StatusCounts
from llama.model_utils.parsed_docs import ParsedDocs
from llama.model_utils.task_writer import TaskWriter
from llama.model_utils.thread_sessions import ThreadSessions
from llama.prompts.base_prompt import Thinking
from llama.prompts.parser_prompt import ParserPrompt
from llama.pylib import fix_ocr, log


def parse_text(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    prompt = ParserPrompt.load(args.prompt, **args)

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
                    call_model,
                    prompt,
                    ocr_result,
                    sessions,
                    args.api_host,
                    args.timeout,
                ): ocr_result
                for ocr_result in docs.tasks
            }
            try:
                for future in as_completed(futures):
                    task_writer.write(
                        future,
                        source=futures[future]["source"],
                        text=futures[future]["text"],
                    )
            finally:
                sessions.close_all()

    logging.info(
        f"Total {len(docs.tasks)} documents processed "
        f"with {statuses.get(ModelStatus.ERROR)} errors "
        f"and {len(docs.already_done)} documents skipped."
    )
    log.job_elapsed(job_began)


def call_model(
    prompt: ParserPrompt,
    ocr_result: dict,
    sessions: ThreadSessions,
    api_host: str,
    timeout: int,
) -> dict:
    began = datetime.now()

    text = fix_ocr.prepare_for_parse(ocr_result["text"])

    extracted = {}
    try:
        session = sessions.get()
        response = session.post(
            f"{api_host}/chat/completions",
            headers=prompt.headers(),
            json=prompt.payload(text),
            timeout=timeout,
        )
        response.raise_for_status()
        result = response.json()

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
    content = content.replace("```json", "").replace("```", "")
    extracted = json.loads(content)
    if not isinstance(extracted, dict):
        raise TypeError("Model response JSON must be an object")
    return extracted


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
    model_group.add_argument(
        "--model-id",
        default="unsloth/Qwen3.6-35B-A3B-MTP-GGUF:UD-Q4_K_XL",
        metavar="string",
        help="""Use this language model. (default: %(default)s) There is a speed vs.
            cost trade off between local and hosted models. Local models are cheaper
            but hosted models are much faster.""",
    )
    model_group.add_argument(
        "--api-host",
        default="http://localhost:9931/v1",
        metavar="string",
        help="""URL for the LM model. (default %(default)s""",
    )
    model_group.add_argument(
        "--threads",
        type=int,
        default=4,
        metavar="int",
        help="""How many parallel threads to run. (default: %(default)s) For
            ChatGPT-nano I will increase this to 20 or more, and for a local model
            I will reduce this to 4 or less.""",
    )
    model_group.add_argument(
        "--temperature",
        type=float,
        metavar="float",
        help="""Model's temperature.""",
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
        default=300,
        metavar="int",
        help="""How long to wait for the LM to respond in seconds.
            (default: %(default)s).""",
    )
    model_group.add_argument(
        "--thinking",
        type=Thinking,
        default=Thinking.DISABLE_TEMPLATE,
        help="""How to handle thinking.""",
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
    return ns


if __name__ == "__main__":
    load_dotenv()
    ARGS = parse_args()
    parse_text(ARGS)
