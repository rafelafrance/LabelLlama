#!/usr/bin/env python3

import argparse
import logging
import textwrap
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from requests.exceptions import RequestException

from llama.prompts.prompt import REQUIRED_COLUMNS, Prompt, Thinking
from llama.pylib import fix_ocr, image_util, log
from llama.results.job_runner import NO_IMAGES_FOUND, run_jobs
from llama.results.model_status import ModelStatus
from llama.results.ocr_docs import OcrDocs

if TYPE_CHECKING:
    from llama.pylib.thread_sessions import ThreadSessions


def ocr_images(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    docs = OcrDocs(args.image_dir, args.image_glob, args.ocr_file, args.limit)

    prompt = Prompt(
        prompt_md=args.prompt_md,
        model_id=args.model_id,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        thinking=args.thinking,
    )
    if set(prompt.columns) != set(REQUIRED_COLUMNS):
        extra = sorted(set(prompt.columns) - set(REQUIRED_COLUMNS))
        msg = (
            f"{args.prompt_md} declares {len(extra)} field(s) "
            f"(e.g. {', '.join(extra[:5])}); ocr_images.py needs a plain OCR prompt "
            "(e.g. prompts/ocr_v2.md)"
        )
        raise ValueError(msg)

    def call(source: Path, sessions: ThreadSessions) -> dict:
        return call_model(
            prompt,
            source,
            sessions,
            args.api_host,
            args.timeout,
            convert_html=args.convert_html,
        )

    run_jobs(
        prompt=prompt,
        out_file=args.ocr_file,
        file_mode=docs.file_mode,
        tasks=docs.tasks,
        skipped=docs.skipped,
        total=docs.image_count,
        unit="image(s)",
        verb="OCRed",
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
    *,
    convert_html: bool,
) -> dict:
    began = datetime.now()

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

        text = fix_ocr.clean_ocr(content, convert_html=convert_html)
        status = ModelStatus.SUCCESS
        if not text:
            text = "The model returned no text"
            status = ModelStatus.ERROR

    except (
        IndexError,
        KeyError,
        OSError,
        RequestException,
        TypeError,
        ValueError,
    ) as err:
        logging.error(f"OCR error for: {Path(source).name}: {str(err)[:120]}")
        text = str(err)
        status = ModelStatus.ERROR

    rec = {
        "status": status,
        "source": str(source),
        "elapsed": str(log.task_elapsed(began)),
        "text": text,
    }

    return rec


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""OCR images."""),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--image-dir",
        type=Path,
        metavar="PATH",
        help="""OCR all images in this directory.""",
    )
    io_group.add_argument(
        "--image-glob",
        metavar="GLOB",
        help="""Get all images matching this glob/pattern. You will need to quote this
            argument. An example: 'museum/data/images1/*.jpg'""",
    )
    io_group.add_argument(
        "--ocr-file",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Put OCRed text into this CSV file. If the file exists then it appends to
            this file.""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt-md",
        type=Path,
        default=Path("prompts/ocr_v2.md"),
        metavar="PATH",
        help="""A markdown file with a prompt used to OCR images.
            (default: %(default)s)""",
    )
    model_group = arg_parser.add_argument_group("model options")
    model_group.add_argument(
        "--model-id",
        default="unsloth/gemma-4-E4B-it-GGUF:Q8_K_XL",
        metavar="STRING",
        help="""Use this language model. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--api-host",
        default="http://localhost:9931/v1",
        metavar="STRING",
        help="""URL for the language model. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--threads",
        type=int,
        default=2,
        metavar="INT",
        help="""How many parallel threads to run. (default: %(default)s)
            Increase this if the model server is powerful enough.""",
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
        default=2048,
        metavar="INT",
        help="""The OCR model's response maximum tokens. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--timeout",
        type=int,
        default=120,
        metavar="INT",
        help="""How long to wait for the OCR model to complete in seconds.
            (default: %(default)s)""",
    )
    model_group.add_argument(
        "--thinking",
        type=Thinking,
        default=Thinking.DISABLE_TEMPLATE,
        help="""How to handle model thinking. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--convert-html",
        action="store_true",
        help="""Convert HTML to text. Some models return HTML only.""",
    )
    logging_group = arg_parser.add_argument_group("logging options")
    logging_group.add_argument(
        "--log-file",
        type=Path,
        metavar="PATH",
        help="""Append logging notices to this file. It also logs the script options
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
        help="""Only OCR this many images.""",
    )
    ns: argparse.Namespace = arg_parser.parse_args(args)
    ns.api_host = ns.api_host.rstrip("/")
    if not ns.image_dir and not ns.image_glob:
        arg_parser.error("one of --image-dir or --image-glob is required")
    if ns.image_dir and not ns.image_dir.is_dir():
        arg_parser.error(f"--image-dir is not a directory: {ns.image_dir}")
    if not ns.prompt_md.is_file():
        arg_parser.error(f"--prompt-md is not a file: {ns.prompt_md}")
    if ns.limit is not None and ns.limit < 1:
        arg_parser.error(f"--limit must be an integer >= 1: {ns.limit}")
    if ns.threads < 1:
        arg_parser.error(f"--threads must be an integer >= 1: {ns.threads}")
    if ns.timeout < 1:
        arg_parser.error(f"--timeout must be an integer >= 1: {ns.timeout} seconds")
    if ns.max_tokens is not None and ns.max_tokens < 1:
        arg_parser.error("--max-tokens must be >= 1")
    if ns.temperature is not None and ns.temperature < 0.0:
        arg_parser.error(f"--temperature must be a float >= 0.0: {ns.temperature}")
    return ns


if __name__ == "__main__":
    load_dotenv()
    ARGS = parse_args()
    log.run_job(ocr_images, ARGS)
