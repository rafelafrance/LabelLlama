#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

from llama.model_utils.parser_prompt import ParserPrompt


def show(args: argparse.Namespace) -> None:
    prompt = ParserPrompt.load(args.prompt)
    print(prompt.system_msg)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Show a prompt."""),
    )
    arg_parser.add_argument(
        "--prompt",
        type=Path,
        required=True,
        metavar="path",
        help="""A markdown file with a prompt and list of fields to parse.
            For example prompts/llm_fields/herbarium_v1.md.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    show(ARGS)
