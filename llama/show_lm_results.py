#!/usr/bin/env python3

import argparse
import base64
import json
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import jinja2
from label_types import herbarium_label as he
from pylib import darwin_core as dwc


@dataclass
class Label:
    type: str
    name: str
    text: str
    url: str
    score: str
    table: list[dict] = field(default_factory=list)


def main(args: argparse.Namespace) -> None:
    with args.predictions_jsonl.open() as f:
        ocr = json.load(f)

    labels = []
    for label in ocr:
        path = Path(label["Source-File"])
        labels.append(
            Label(
                type=path.stem.split("_")[1],
                name=path.stem,
                text=dwc.format_text_as_html(label["text"]),
                url=encode_label(args.label_dir, path),
                score=f"{label['total_score']:0.2f}",
                table=results_to_table(label),
            )
        )

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("./llama/templates"),
        autoescape=True,
    )

    template = env.get_template("show_lm_results.html").render(
        now=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M"),
        jsonl_file=args.predictions_jsonl,
        label_dir=args.label_dir,
        labels=labels,
    )

    with args.output_html.open("w") as html_file:
        html_file.write(template)


def results_to_table(label: dict[str, Any]) -> list[dict]:
    fields = zip(
        label["trues"].keys(),
        label["trues"].values(),
        label["preds"].values(),
        label["scores"].values(),
        strict=True,
    )
    rows = []
    for key, true, pred, score in fields:
        yellow = 0.5
        if score == 1.0 and true:
            color = "green"
        elif score == 1.0 and not true:
            color = ""
        elif score > yellow:
            color = "yellow"
        else:
            color = "red"
        rows.append(
            {
                "key": he.DWC[key],
                "true": "<br/>".join(true),
                "pred": "<br/>".join(pred),
                "score": f"{score:0.2f}",
                "color": color,
            }
        )
    return rows


def encode_label(label_dir: Path, ocr_path: Path) -> str:
    path = label_dir / ocr_path.name
    with path.open("rb") as f:
        url = base64.b64encode(f.read()).decode()
    return url


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Show pipeline results."""),
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
        help="""Output the pipeline results to this HTML file.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
