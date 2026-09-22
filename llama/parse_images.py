#!/usr/bin/env python3

"""Extract text information from images of museum specimens using a single model."""

import argparse
import logging
import textwrap
from datetime import datetime
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from requests.exceptions import RequestException

from llama.prompts.prompt import Prompt, Thinking
from llama.pylib import image_util, log
from llama.results.job_runner import NO_IMAGES_FOUND, run_jobs
from llama.results.model_status import ModelStatus
from llama.results.ocr_docs import OcrDocs

if TYPE_CHECKING:
    from llama.pylib.thread_sessions import ThreadSessions


def extract(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    prompt = Prompt(
        prompt_md=args.prompt_md,
        model_id=args.model_id,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        thinking=args.thinking,
    )
    prompt.must_have_llm_fields()

    docs = OcrDocs(args.image_dir, args.image_glob, args.parsed_file, args.limit)

    def call(source: Path, sessions: ThreadSessions) -> dict:
        return call_model(prompt, source, sessions, args.api_host, args.timeout)

    run_jobs(
        prompt=prompt,
        out_file=args.parsed_file,
        file_mode=docs.file_mode,
        tasks=docs.tasks,
        skipped=docs.skipped,
        total=docs.image_count,
        unit="image(s)",
        verb="Extracted",
        nothing_found=NO_IMAGES_FOUND,
        call=call,
        threads=args.threads,
        job_began=job_began,
    )


def call_model(
    prompt: Prompt,
    source: Path | str,
    sessions: ThreadSessions,
    api_host: str,
    timeout: int,
) -> dict:
    began = datetime.now()

    extracted = {}
    response = None

    try:
        base64_image, mime_type = image_util.load_image(source)

        session = sessions.get()
        response = session.post(
            f"{api_host}/chat/completions",
            headers=prompt.headers(),
            json=prompt.image_payload(mime_type, base64_image),
            timeout=timeout,
        )
        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"] or ""

        text = content
        extracted = prompt.parse_model_json(content)

        status = ModelStatus.SUCCESS

    except JSONDecodeError as err:
        # response.json() can fail too, in which case we never saw any content,
        # so quote the body that actually arrived.
        logging.error(f"Extract error for: {Path(source).name}: {str(err)[:120]}")
        body = response.text[:200] if response is not None else ""
        text = f"{err} :: {body}" if body else str(err)
        status = ModelStatus.ERROR
    except (
        AttributeError,
        IndexError,
        KeyError,
        OSError,
        RequestException,
        TypeError,
        ValueError,
    ) as err:
        logging.error(f"Extract error for: {Path(source).name}: {str(err)[:120]}")
        text = str(err)
        status = ModelStatus.ERROR

    result = {
        "status": status,
        "source": str(source),
        "elapsed": str(log.task_elapsed(began)),
        "text": text,
    } | prompt.validated_fields(extracted, str(source))

    return result


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
        "--parsed-file",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Write the LM results to this CSV file.
            This appends data to the file.""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt-md",
        type=Path,
        required=True,
        metavar="PATH",
        help="""A markdown file with a prompt and list of fields to parse.
            For example prompts/diode_one_v1.md.""",
    )
    model_group = arg_parser.add_argument_group("model options")
    model_group.add_argument(
        "--model-id",
        default="unsloth/Qwen3.6-35B-A3B-MTP-GGUF:UD-Q4_K_XL",
        metavar="STRING",
        help="""Use this language model. (default: %(default)s) There is a speed vs.
            cost trade off between local and hosted models. Local models are cheaper
            but hosted models are much faster. The model must support images.""",
    )
    model_group.add_argument(
        "--api-host",
        default="http://localhost:9931/v1",
        metavar="STRING",
        help="""URL for the LM model. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--threads",
        type=int,
        default=4,
        metavar="INT",
        help="""How many parallel threads to run. (default: %(default)s) For
            ChatGPT-nano I will increase this to 20 or more, and for a local model
            I will reduce this to 4 or less.""",
    )
    model_group.add_argument(
        "--temperature",
        type=float,
        metavar="FLOAT",
        help="""Model's temperature.""",
    )
    model_group.add_argument(
        "--max-tokens",
        type=int,
        metavar="INT",
        help="""The model's response maximum tokens.
            I use this to truncate model loops.""",
    )
    model_group.add_argument(
        "--timeout",
        type=int,
        default=300,
        metavar="INT",
        help="""How long to wait for the LM to respond in seconds.
            (default: %(default)s) 5 minutes is a life time for extracting data
            from an image.""",
    )
    model_group.add_argument(
        "--thinking",
        type=Thinking,
        default=Thinking.DISABLE_TEMPLATE,
        help="""How to handle model thinking. (default: %(default)s)""",
    )
    logging_group = arg_parser.add_argument_group("logging options")
    logging_group.add_argument(
        "--log-file",
        type=Path,
        metavar="PATH",
        help="""Append logging notices to this file. It also logs the script arguments
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
        help="""Limit to this many images.""",
    )
    ns = arg_parser.parse_args(args)
    if not ns.image_dir and not ns.image_glob:
        arg_parser.error("one of --image-dir or --image-glob is required")
    if ns.image_dir and not ns.image_dir.is_dir():
        arg_parser.error(f"--image-dir is not a directory: {ns.image_dir}")
    if not ns.prompt_md.is_file():
        arg_parser.error(f"--prompt-md is not a file: {ns.prompt_md}")
    if ns.threads < 1:
        arg_parser.error("--threads must be >= 1")
    if ns.timeout < 1:
        arg_parser.error("--timeout must be >= 1")
    if ns.max_tokens is not None and ns.max_tokens < 1:
        arg_parser.error("--max-tokens must be >= 1")
    if ns.limit is not None and ns.limit < 1:
        arg_parser.error("--limit must be >= 1")
    if ns.temperature is not None and ns.temperature < 0.0:
        arg_parser.error(f"--temperature must be a float >= 0.0: {ns.temperature}")
    return ns


if __name__ == "__main__":
    load_dotenv()
    ARGS = parse_args()
    log.run_job(extract, ARGS)
