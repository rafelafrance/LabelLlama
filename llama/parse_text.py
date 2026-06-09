#!/usr/bin/env python3

import argparse
import logging
import os
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from tqdm import tqdm

from llama.pylib import io_util, preprocess, prompt_util, str_util, timer

DEFAULT_POOL = 10


def lm_extract(args: argparse.Namespace) -> None:
    job_began = timer.job_began(args.log_file, args=args)

    prompt = prompt_util.Prompt.load(args.prompt)
    field_prompts = prompt.build_field_prompts()
    field_template = prompt.build_field_template()
    column_names = prompt.column_names()

    docs = io_util.read_list_of_dicts(args.ocr_file, fill_na="", limit=args.limit)
    docs = [d for d in docs if d["status"] == "success"]

    char_len = len(prompt.system_prompt) + len(field_prompts) + len(field_template)
    word_len = (
        len(prompt.system_prompt.split())
        + len(field_prompts.split())
        + len(field_template.split())
    )
    logging.info(
        f"The prompt length (without label text) is {char_len} characters, "
        f"{word_len} words"
    )

    with requests.Session() as session, tqdm(total=len(docs)) as pbar:
        if args.threads > DEFAULT_POOL:
            adapter = HTTPAdapter(
                pool_connections=args.threads, pool_maxsize=args.threads
            )
            session.mount("http://", adapter)
            session.mount("https://", adapter)

        results = []

        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = {
                executor.submit(
                    call_lm,
                    args,
                    doc,
                    session,
                    prompt,
                    field_prompts,
                    field_template,
                    column_names,
                ): doc
                for doc in docs
            }
            for future in as_completed(futures):
                results.append(future.result())
                pbar.update(1)

    errors = sum(1 for r in results if r["status"] == "ERROR")
    results = sorted(results, key=lambda r: r["source"])

    logging.info(f"Total {len(results)} documents processed with {errors} errors.")

    io_util.output_file(args.parse_file, results)

    timer.job_elapsed(job_began)


def call_lm(
    args: argparse.Namespace,
    doc: dict,
    session: requests.Session,
    prompt: prompt_util.Prompt,
    field_prompts: str,
    field_template: str,
    column_names: list[str],
) -> dict:
    began = datetime.now()

    text = preprocess.clean_text(doc["text"])

    url = f"{args.api_host}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('LLM_API_KEY')}",
    }
    payload = {
        "model": args.model,
        "messages": [
            # {"role": "system", "content": str(began)},  # Defeat cache
            {"role": "system", "content": prompt.system_prompt},
            {"role": "user", "content": field_prompts},
            {"role": "user", "content": field_template},
            {"role": "user", "content": prompt_util.Prompt.build_text_prompt(text)},
        ],
    }
    if args.temperature is not None:
        payload["temperature"] = args.temperature
    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens

    try:
        response = session.post(
            url, headers=headers, json=payload, timeout=args.timeout
        )
        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"] or ""
        extracted = str_util.llm_reply_to_dict(content, column_names)

        status = "success"

    except requests.exceptions.RequestException as err:
        logging.exception("API error")
        extracted = {"ERROR": str(err)}
        status = "ERROR"

    result = {
        "status": status,
        "source": doc["source"],
        "text": text,
        "elapsed": str(timer.task_elapsed(began)),
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
            columns for valid input, so any CSV/TSV/JSON/JSONL file with those columns
            is fine.""",
    )
    io_group.add_argument(
        "--parse-file",
        type=Path,
        metavar="path",
        help="""Write the LM results to this file.
           Handles (.json, .jsonl, .csv, .tsv)""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt",
        type=Path,
        required=True,
        metavar="path",
        help="""A markdown file with a prompt and list of fields to parse.
            For example prompts/fields/herbarium.md.""",
    )
    model_group = arg_parser.add_argument_group("model options")
    model_group.add_argument(
        "--model",
        default="lm_studio/google/gemma-4-26b-a4b",
        metavar="string",
        help="""Use this language model. (default: %(default)s) There is a speed vs.
            cost tradeoff between local and hosted models. Local models are cheaper
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
            I will reduce this to 4.""",
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
        help="""The LM response's maximum tokens. Some hosted servers are OK with you
            not setting this so, I don't have a default.""",
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
    lm_extract(ARGS)
