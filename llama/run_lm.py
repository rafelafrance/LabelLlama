#!/usr/bin/env python3

import argparse
import asyncio
import json
import logging
import textwrap
from datetime import datetime
from pathlib import Path

import dspy
from openai import APIError, AsyncOpenAI

from llama.llm.dwc_module import DwcModule
from llama.llm.signature_registry import SIGNATURE_REGISTRY
from llama.pylib import io_util, preprocess, prompt_util, timer
from llama.pylib.str_util import strip_json_fences

JSON_ERRORS = (json.JSONDecodeError, UnicodeDecodeError)

SEMAPHORE: asyncio.Semaphore = asyncio.Semaphore(1)


def lm_extract(args: argparse.Namespace) -> None:
    job_began = timer.job_began(args.log_file, args=args)

    lm = dspy.LM(
        args.model,
        api_base=args.api_host,
        api_key=args.api_key,
        temperature=args.temperature,
    )
    dspy.configure(lm=lm)

    predictor = DwcModule(args.signature)

    # prompt = dspy.ChatAdapter().format_system_message(predictor.signature)
    # print(prompt)

    parallel = dspy.Parallel(num_threads=args.threads)

    docs = io_util.read_list_of_dicts(args.docs, fill_na="")

    exec_pairs = [
        (predictor, {"text": preprocess.clean_text(d["text"]), "source": d["source"]})
        for d in docs
    ]

    results = parallel(exec_pairs)

    io_util.output_file(args.out_file, results)

    timer.job_elapsed(job_began)


async def new_lm_extract(args: argparse.Namespace) -> None:
    global SEMAPHORE

    job_began = timer.job_began(args.log_file, args=args)

    SEMAPHORE = asyncio.Semaphore(args.threads)
    sys_prompt, field_list = prompt_util.read_field_list_prompts(args.prompt)
    field_prompts = prompt_util.get_field_prompts(field_list)
    docs = io_util.read_list_of_dicts(args.docs, fill_na="")

    async with AsyncOpenAI() as client:
        tasks = [call_lm(args, doc, client, sys_prompt, field_prompts) for doc in docs]

    results = await asyncio.gather(*tasks)

    errors = sum(1 for r in results if "ERROR" in r)
    logging.info(f"Total {len(results)} documents processes with {errors} errors.")

    io_util.output_file(args.out_file, results)

    timer.job_elapsed(job_began)


async def call_lm(
    args: argparse.Namespace,
    doc: dict,
    client: AsyncOpenAI,
    sys_prompt: str,
    field_prompts: str,
) -> dict:
    async with SEMAPHORE:
        began = datetime.now()

        text = preprocess.clean_text(doc["text"])

        try:
            response = await client.chat.completions.create(
                model=args.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": field_prompts},
                    {"role": "user", "content": f"`text` (str):\n{text}"},
                ],
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )

            content = response.choices[0].message.content or ""
            content = strip_json_fences(content)

        except APIError as err:
            logging.exception("API error")
            content = json.dumps({"ERROR": str(err)})

        if not content:
            content = json.dumps({"ERROR": "Nothing returned by LM."})

        try:
            result = json.loads(content)
        except JSON_ERRORS:
            result = {"ERROR": "Invalid JSON returned by LM."}

        elapsed = timer.elapsed(began)

        result = {"source": doc["source"], "text": text, "elapsed": elapsed} | result

        return result


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Use a language model (LM) to extract information from text."""
        ),
    )
    signatures = list(SIGNATURE_REGISTRY.keys())
    arg_parser.add_argument(
        "--signature",
        choices=signatures,
        default=signatures[0],
        help="""What type of data are you extracting? What is its signature?""",
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
        "--api-key",
        help="""API key.""",
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
    # lm_extract(ARGS)
    asyncio.run(new_lm_extract(ARGS))
