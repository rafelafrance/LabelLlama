#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

from accelerate import Accelerator
from transformers import pipeline

from llama.prompts.prompt_markdown_parser import PromptMarkdownParser
from llama.pylib import log
from llama.results.ocr_docs import OcrDocs


def ocr_images(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    docs = OcrDocs(args.image_dir, args.image_glob, args.ocr_file, args.limit)

    prompt_data = PromptMarkdownParser(args.prompt_md)

    pipe = pipeline(
        "image-text-to-text",
        model=args.model_id,
        device=Accelerator().device,
        max_new_tokens=args.max_tokens,
        num_workers=args.threads,
        batch_size=args.batch_size,
        enable_thinking=False,
    )

    print()
    messages = [
        [
            {"role": "system", "content": prompt_data.system_msg},
            {"role": "user", "content": [{"type": "image", "url": str(p)}]},
        ]
        for p in docs.tasks
    ]
    for result in pipe(messages):
        messages = result[0].get("generated_text", "")
        if messages:
            output = next(
                m.get("content", "")
                for m in messages
                if m.get("role", "").lower() == "assistant"
            )
            print("=" * 80)
            print(output)
            print()

    log.job_elapsed(job_began)


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
        default="google/gemma-4-E4B-it-GGUF:Q8_K_XL",
        metavar="STRING",
        help="""Use this language model. (default: %(default)s)""",
    )
    model_group.add_argument(
        "--batch-size",
        type=int,
        default=1,
        metavar="INT",
        help="""Pass this many images to the model at a time. (default: %(default)s)""",
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
        "--max-tokens",
        type=int,
        default=2048,
        metavar="INT",
        help="""The OCR model's response maximum tokens. (default: %(default)s)""",
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
    if ns.max_tokens is not None and ns.max_tokens < 1:
        arg_parser.error("--max-tokens must be >= 1")
    if ns.batch_size < 1:
        arg_parser.error(f"--batch-size must be an integer >= 1: {ns.batch_size}")
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    ocr_images(ARGS)
