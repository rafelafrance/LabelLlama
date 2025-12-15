#!/usr/bin/env python3

import argparse
import base64
import json
import textwrap
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import jinja2

# from pprint import pp


@dataclass
class OcrResult:
    image_path: str
    image_base64: str
    ocr_results: list[dict]


def main(args: argparse.Namespace) -> None:
    ocr_results: dict[str, list[OcrResult]] = defaultdict(list)
    images_base64: dict[str, str] = {}
    with args.input_jsonl.open() as f:
        for ln in f.readlines():
            result = json.loads(ln)
            image_path = result["image_path"]
            ocr_results[image_path].append(result)
            if image_path not in images_base64:
                images_base64[image_path] = encode_sheet(image_path)

    rec0 = next(iter(ocr_results.values()))
    headers = sorted(r["model_name"] for r in rec0)

    output = []
    for image_path, results in ocr_results.items():
        results = sorted(results, key=lambda r: r["model_name"])
        results = [r["prediction"].replace("\n", "<br/>") for r in results]
        output.append(
            OcrResult(
                image_path=image_path,
                image_base64=images_base64[image_path],
                ocr_results=results,
            )
        )

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("./llama/templates"),
        autoescape=True,
    )

    template = env.get_template("ocr_compare_report.html").render(
        now=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M"),
        jsonl_file=args.input_jsonl,
        ocr_results=output,
        headers=headers,
    )

    with args.output_html.open("w") as html_file:
        html_file.write(template)


def encode_sheet(image_path: str) -> str:
    with Path(image_path).open("rb") as f:
        url = base64.b64encode(f.read()).decode()
    return url


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Show OCR results."""),
    )

    arg_parser.add_argument(
        "--input-jsonl",
        type=Path,
        metavar="PATH",
        help="""The output of the OCR engines are in this JSONL file.""",
    )

    arg_parser.add_argument(
        "--output-html",
        type=Path,
        metavar="PATH",
        help="""Output the OCR results to this HTML file.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
