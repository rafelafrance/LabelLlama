#!/usr/bin/env python3

import argparse
import csv
import logging
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from requests.exceptions import RequestException
from tqdm import tqdm

from llama.model_utils.model_status import ModelStatus, StatusCounts
from llama.model_utils.ocr_docs import OcrDocs
from llama.model_utils.task_writer import TaskWriter
from llama.model_utils.thread_sessions import ThreadSessions
from llama.prompts.base_prompt import Thinking
from llama.prompts.ocr_prompt import OcrPrompt
from llama.pylib import fix_ocr, image_util, log


def ocr_images(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    prompt = OcrPrompt(args.prompt, **args)

    docs = OcrDocs.build(args.image_dir, args.image_glob, args.ocr_file, args.limit)

    if args.input_file:
        docs.tasks += [
            s
            for s in image_util.read_sources(args.input_file)
            if str(s) not in docs.already_done
        ]

    logging.info(f"There are {docs.input_len} images to process")
    logging.info(f"{len(docs.already_done)} images were already done.")
    if docs.limit:
        logging.info(f"Limited to {docs.limit} images.")
    logging.info(f"There are {len(docs.tasks)} images left to process.")

    statuses = StatusCounts()

    with args.ocr_file.open(docs.file_mode) as output_file:
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
                    call_model, prompt, source, sessions, args.api_host, args.timeout
                ): source
                for source in docs.tasks
            }

            try:
                for future in as_completed(futures):
                    task_writer.write(future, source=futures[future])
            finally:
                sessions.close_all()

    logging.info(
        f"Total {len(docs.tasks)} images processed "
        f"with {statuses.get(ModelStatus.ERROR)} errors "
        f"and {len(docs.already_done)} images skipped."
    )
    log.job_elapsed(job_began)


def call_model(
    prompt: OcrPrompt,
    source: Path | str,
    sessions: ThreadSessions,
    api_host: str,
    timeout: int,
) -> dict:
    began = datetime.now()

    try:
        base64_image, mime_type = image_util.load_image(source, timeout)

        session = sessions.get()
        response = session.post(
            f"{api_host}/chat/completions",
            headers=prompt.headers(),
            prompt=prompt.payload(mime_type, base64_image),
            timeout=timeout,
        )
        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"] or ""

        text = fix_ocr.clean_ocr(content)
        status = ModelStatus.SUCCESS

    except (
        IndexError,
        KeyError,
        OSError,
        RequestException,
        TypeError,
        ValueError,
    ) as err:
        logging.exception(f"OCR error for: {source}")
        text = str(err)
        status = ModelStatus.ERROR

    result = {
        "status": status,
        "source": str(source),
        "elapsed": str(log.task_elapsed(began)),
        "text": text,
    }

    return result


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
        "--input-file",
        type=Path,
        metavar="PATH",
        help="""Read a list of image sources (local paths and/or http(s) URLs)
            from this file, one source per line. Blank lines and lines starting
            with '#' are ignored. Can be combined with --image-dir /
            --image-glob, or used on its own.""",
    )
    io_group.add_argument(
        "--ocr-file",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Put OCRed text into this CSV file. This appends data to the file.""",
    )
    prompt_group = arg_parser.add_argument_group("prompt options")
    prompt_group.add_argument(
        "--prompt",
        type=Path,
        default="prompts/ocr_v2.md",
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
            (default: %(default)s) 2 minutes is a life time for OCR.""",
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
    if not ns.image_dir and not ns.image_glob and not ns.input_file:
        arg_parser.error(
            "one of --image-dir, --image-glob, or --input-file is required"
        )
    if ns.image_dir and not ns.image_dir.is_dir():
        arg_parser.error(f"--image-dir is not a directory: {ns.image_dir}")
    return ns


if __name__ == "__main__":
    load_dotenv()
    ARGS = parse_args()
    ocr_images(ARGS)
