#!/usr/bin/env python3

import argparse
import logging
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests
from tqdm import tqdm

from llama.pylib import io_util, preprocess, prompt_util, str_util, timer


def lm_extract(args: argparse.Namespace) -> None:

    job_began = timer.job_began(args.log_file, args=args)

    sys_prompt, field_list = prompt_util.read_lm_prompt(args.prompt)
    field_prompts = prompt_util.build_field_prompts(field_list)
    field_template = prompt_util.build_field_template(field_list)
    field_classes = prompt_util.field_classes_by_column_name(field_list)
    column_names = list(field_classes.keys())

    docs = io_util.read_list_of_dicts(args.docs, fill_na="", limit=args.limit)

    char_len = len(sys_prompt) + len(field_prompts) + len(field_template)
    word_len = (
        len(sys_prompt.split())
        + len(field_prompts.split())
        + len(field_template.split())
    )
    logging.info(
        f"The prompt length (without label text) is {char_len} characters, "
        f"{word_len} words"
    )

    with requests.Session() as session, tqdm(total=len(docs)) as pbar:
        results = []

        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = {
                executor.submit(
                    call_lm,
                    args,
                    doc,
                    session,
                    sys_prompt,
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
    good = [r for r in results if r["status"] != "ERROR"]

    logging.info(f"Total {len(results)} documents processed with {errors} errors.")

    io_util.output_file(args.out_file, good)

    timer.job_elapsed(job_began)


def call_lm(
    args: argparse.Namespace,
    doc: dict,
    session: requests.Session,
    sys_prompt: str,
    field_prompts: str,
    field_template: str,
    column_names: list[str],
) -> dict:
    began = datetime.now()

    text = preprocess.clean_text(doc["text"])

    url = f"{args.api_host}/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": field_prompts},
            {"role": "user", "content": field_template},
            {"role": "user", "content": prompt_util.build_text_prompt(text)},
        ],
    }
    if args.temperature is not None:
        payload["temperature"] = args.temperature

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
    arg_parser.add_argument(
        "--prompt",
        type=Path,
        required=True,
        help="""A markdown file with a prompt and list of fields to parse.""",
    )
    arg_parser.add_argument(
        "--docs",
        type=Path,
        help="""Parse doc text from this file. We need only 'source' and 'text'
            columns for valid input, so any file with those columns are fine.""",
    )
    arg_parser.add_argument(
        "--out-file",
        type=Path,
        help="""Write the LM results to this file.
           Handles (.json, .jsonl, .csv, .tsv)""",
    )
    arg_parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="""How long to wait for the LM to respond in seconds.
            (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--threads",
        type=int,
        default=10,
        help="""How many parallel threads to run. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--model",
        default="lm_studio/google/gemma-4-26b-a4b",
        help="""Use this language model. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--api-host",
        # default="http://localhost:1234/v1",
        help="""URL for the LM model.""",
    )
    arg_parser.add_argument(
        "--temperature",
        type=float,
        help="""Model's temperature.""",
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
        help="""Limit to this many records. Primarily for debugging.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    lm_extract(ARGS)
