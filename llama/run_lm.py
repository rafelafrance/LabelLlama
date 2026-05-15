#!/usr/bin/env python3

import argparse
import asyncio
import logging
import textwrap
from datetime import datetime
from pathlib import Path

from openai import APIError, AsyncOpenAI
from tqdm.asyncio import tqdm_asyncio

from llama.pylib import io_util, preprocess, prompt_util, str_util, timer

SEMAPHORE: asyncio.Semaphore = asyncio.Semaphore(1)


async def new_lm_extract(args: argparse.Namespace) -> None:
    global SEMAPHORE

    job_began = timer.job_began(args.log_file, args=args)

    SEMAPHORE = asyncio.Semaphore(args.threads)
    sys_prompt, field_list = prompt_util.read_field_list_prompts(args.prompt)
    field_prompts = prompt_util.get_field_prompts(field_list)
    field_template = prompt_util.get_field_template(field_list)
    docs = io_util.read_list_of_dicts(args.docs, fill_na="", limit=args.limit)

    async with AsyncOpenAI() as client:
        tasks = [
            call_lm(
                args, doc, client, sys_prompt, field_prompts, field_template, field_list
            )
            for doc in docs
        ]
        results = await tqdm_asyncio.gather(*tasks)

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
    field_template: str,
    field_list: list[str],
) -> dict:
    async with SEMAPHORE:
        began = datetime.now()

        text = preprocess.clean_text(doc["text"])

        try:
            response = await client.chat.completions.create(
                model=args.model,
                messages=[
                    # {"role": "system", "content": str(datetime.now())}, # Defeat cache
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": field_prompts},
                    {"role": "user", "content": field_template},
                    {"role": "user", "content": prompt_util.get_text_prompt(text)},
                ],
                temperature=args.temperature,
            )

            content = response.choices[0].message.content or ""
            results = str_util.llm_reply_to_dict(content, field_list)

        except APIError as err:
            logging.exception("API error")
            results = {"ERROR": str(err)}

        elapsed = timer.elapsed(began)

        result = {"source": doc["source"], "text": text, "elapsed": elapsed} | results

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
    asyncio.run(new_lm_extract(ARGS))
