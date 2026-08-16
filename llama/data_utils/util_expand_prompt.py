#!/usr/bin/env python3

import argparse
import re
import textwrap
from pathlib import Path

import yaml

from llama.pylib.prompt_file_parser import PromptFileParser


def expand_prompt(args: argparse.Namespace) -> None:
    prompt = PromptFileParser.load(args.prompt)
    paths = [str(f.module) for f in prompt.llm_fields]
    paths = [p.replace("../llama/fields", "prompts/fields_v2") for p in paths]
    paths = [p.replace(".py", "_v2.md") for p in paths]
    fields = []
    for path in paths:
        path = Path(path)
        with path.open() as fin:
            text = fin.read()
        front = get_front_yaml(text, path)
        prop = f"""
                "{front["name"]}": {{
                    "type": "string",
                    "description": "{front["description"]}"
                }}"""
        fields.append(prop)
    prefix = """
        {
            "type": "object",
            "properties": {
        """
    suffix = """
            }
        }
    """
    template = prefix + ",".join(fields) + suffix
    template = textwrap.dedent(template)
    print(template)


def get_front_yaml(text: str, path: Path) -> dict:
    top = re.search("^---$.*^---$", text, flags=re.MULTILINE | re.DOTALL)
    if not top:
        raise ValueError(f"Improperly formatted prompt file. {path}")

    top = top.group(0).replace("---", "")
    front = yaml.safe_load(top)
    return front


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""
            I want to see the fully expanded prompt. Without the payload.
            """),
    )
    arg_parser.add_argument(
        "--prompt",
        type=Path,
        default="prompts/ocr_v2.md",
        metavar="PATH",
        help="""A markdown file with a prompt used to OCR images.
            (default: %(default)s)""",
    )
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    expand_prompt(ARGS)
