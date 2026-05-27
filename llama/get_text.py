#!/usr/bin/env python3

import argparse
import asyncio
import base64
import contextlib
import logging
import textwrap
from datetime import datetime
from pathlib import Path

import pandas as pd
from openai import APIError, AsyncOpenAI
from tqdm.asyncio import tqdm_asyncio

from llama.pylib import io_util, prompt_util, str_util, timer

SEMAPHORE: asyncio.Semaphore = asyncio.Semaphore(1)


async def async_ocr_images(args: argparse.Namespace) -> None:
    global SEMAPHORE

    job_began = timer.job_began(args.log_file, args=args)

    already_read = get_docs_already_read(args.docs)

    glob = (args.glob or "*") + ".[Jj][Pp][Gg]"
    image_paths = sorted(args.image_dir.glob(glob))
    image_paths = image_paths[: args.limit]
    logging.info(f"There are images {len(image_paths)} to OCR")

    sys_prompt = prompt_util.read_prompt(args.prompt)
    logging.info(
        f"System prompt length (without image) = {len(sys_prompt)} characters, "
        f"{len(sys_prompt.split())} words"
    )

    SEMAPHORE = asyncio.Semaphore(args.threads)

    async with AsyncOpenAI(base_url=args.api_host) as client:
        tasks = [
            call_ocr(args, image_path, client, sys_prompt)
            for image_path in image_paths
            if image_path not in already_read
        ]

        results = await tqdm_asyncio.gather(*tasks)

    errors = sum(1 for r in results if "ERROR" in r)

    good = [r for r in results if "ERROR" not in r]
    for row in good:
        row["text"] = str_util.clean_ocr(row["text"])

    logging.info(
        f"Total {len(results)} documents processed with {errors} errors "
        f"and {len(already_read)} documents were skipped."
    )

    io_util.output_file(args.docs, good, mode="a")

    timer.job_elapsed(job_began)


async def call_ocr(
    args: argparse.Namespace,
    image_path: Path,
    client: AsyncOpenAI,
    sys_prompt: str,
) -> dict:
    async with SEMAPHORE:
        began = datetime.now()

        try:
            with image_path.open("rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            response = await client.chat.completions.create(
                model=args.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}",
                                },
                            },
                        ],
                    },
                ],
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )

            text = response.choices[0].message.content or ""
            result = {"source": str(image_path), "text": text}

        except APIError as err:
            logging.exception("API error")
            result = {"ERROR": str(err)}

        elapsed = timer.elapsed(began)
        result["elapsed"] = elapsed

        return result


def get_docs_already_read(docs: Path) -> list[Path]:
    done = []
    if docs.exists():
        with contextlib.suppress(pd.errors.EmptyDataError):
            records = io_util.read_list_of_dicts(docs)
            done = [Path(r["source"]) for r in records if r.get("source")]
    return done


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""OCR images."""),
    )
    arg_parser.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        help="""Directory containing all of the images to OCR.""",
    )
    arg_parser.add_argument(
        "--docs",
        type=Path,
        required=True,
        help="""Put OCRed text into this file. This appends data to the file.""",
    )
    arg_parser.add_argument(
        "--model",
        default="chandra-ocr",
        help="""Use this language model. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--prompt",
        type=Path,
        default="prompts/ocr.md",
        help="""A markdown file with a prompt used to OCR images.
            (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--api-host",
        default="http://localhost:1234/v1",
        help="""URL for the language model. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--max-tokens",
        type=int,
        help="""The LM response's maximum tokens.""",
    )
    arg_parser.add_argument(
        "--threads",
        type=int,
        default=2,
        help="""How many parallel threads to run. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="""Model's temperature. (default: %(default)s)""",
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
        "--glob",
        help="""Only get images matching this glob.
            For now, I am appending an additional file suffix glob.""",
    )
    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Only read this many records.""",
    )
    ns: argparse.Namespace = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    asyncio.run(async_ocr_images(ARGS))
