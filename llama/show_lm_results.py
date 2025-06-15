#!/usr/bin/env python3

import argparse
import base64
import json
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import jinja2

# from pprint import pp

RELABEL = {
    "sci_name": "Scientific name",
    "sci_authority": "Scientific authority",
    "family": "Taxonomic family",
    "collection_date": "Collection date",
    "locality": "Collected from this locality",
    "habitat": "Collected from this habitat",
    "elevation": "Elevation",
    "lat_long": "Latitude and longitude",
    "trs": "Township Range Section (TRS)",
    "utm": "Universal Transverse Mercator (UTM)",
    "admin_units": "Administrative units",
    "collector_names": "Collector names",
    "collector_id": "Collector ID",
    "determiner_names": "Determiners names",
    "determiner_id": "Determiner ID",
    "id_number": "Specimen ID",
    "assoc_taxa": "Associated taxa",
    "other_obs": "Other observations",
}


@dataclass
class Label:
    type: str
    name: str
    text: str
    url: str
    results: dict[str, str] = field(default_factory=dict)


def main(args):
    with args.predictions_jsonl.open() as f:
        ocr = [json.loads(ln) for ln in f]

    labels = []
    for label in ocr:
        path = Path(label["Source-File"])
        type_ = path.stem.split("_")[1]
        url = encode_label(args.label_dir, path)
        text = format_text(label["text"])
        results = {
            RELABEL.get(k, k): format_text(v)
            for k, v in label.items()
            if k not in ("Source-File", "text")
        }
        labels.append(
            Label(type=type_, name=path.stem, text=text, url=url, results=results)
        )

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("./llama/templates"),
        autoescape=True,
    )

    template = env.get_template("show_lm_results.html").render(
        now=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M"),
        jsonl_file=args.predictions_jsonl,
        label_dir=args.label_dir,
        rows=labels,
    )

    with args.output_html.open("w") as html_file:
        html_file.write(template)


def format_text(text):
    if not isinstance(text, str):
        return text
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
