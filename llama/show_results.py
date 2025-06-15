#!/usr/bin/env python3

import argparse
import base64
import json
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import jinja2

# from pprint import pp


@dataclass
class Label:
    type: str
    name: str
    text: str
    url: str


def main(args):
    with args.predictions_jsonl.open() as f:
        ocr = [json.loads(ln) for ln in f]

    labels = []
    for label in ocr:
        path = Path(label["Source-File"])
        type_ = path.stem.split("_")[1]
        url = encode_label(args.label_dir, path)
        text = format_text(label["text"])
        labels.append(Label(type=type_, name=path.stem, text=text, url=url))

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("./llama/templates"),
        autoescape=True,
    )

    template = env.get_template("show_ocr.html").render(
        now=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M"),
        jsonl_file=args.olmocr_jsonl,
        label_dir=args.label_dir,
        rows=labels,
    )

    with args.output_html.open("w") as html_file:
        html_file.write(template)


def format_text(text):
    text = text.replace("\n", "<br/>")
    return text


def encode_label(label_dir, ocr_path):
    path = label_dir / ocr_path.name
    with path.open("rb") as f:
        url = base64.b64encode(f.read()).decode()
    return url


def parse_args():
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Show language model results."""),
    )

    arg_parser.add_argument(
        "--label-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Images of labels are in this directory.""",
    )

    arg_parser.add_argument(
        "--predictions-jsonl",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Language model predictions JSONL file.""",
    )

    arg_parser.add_argument(
        "--output-html",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output the label images with OCR text to this HTML file.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
