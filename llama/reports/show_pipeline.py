#!/usr/bin/env python3

import argparse
import html
import logging
import textwrap
from datetime import datetime
from pathlib import Path

import jinja2
import pandas as pd

from llama.pylib import image_util, log

TEMPLATES_DIR = Path(__file__).parent / "templates"


def load_template() -> jinja2.Template:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
        autoescape=True,
    )
    return env.get_template("show_pipeline.html")


def image_html(source: str) -> tuple[str, bool]:
    """Return (html for the embedded image, ok) for one record."""
    try:
        base64_image, mime_type = image_util.downscale(source)
    except image_util.IMAGE_ERRORS:
        logging.warning(f"Image unavailable: {source}")
        return '<p class="placeholder">Image unavailable</p>', False
    alt = html.escape(source, quote=True)
    return f'<img src="data:{mime_type};base64,{base64_image}" alt="{alt}">', True


def build_card(number: int, ocr_row: dict, clean_row: dict | None) -> dict:
    source = ocr_row["source"]

    badges = []
    status = ocr_row.get("status", "").strip()
    if status and status.lower() != "success":
        badges.append({"kind": "error", "label": f"OCR status: {status}"})
    if clean_row is None:
        badges.append({"kind": "warn", "label": "Not in cleaned data"})

    img, ok = image_html(source)

    if clean_row is None:
        fields: list[tuple[str, str]] = []
    else:
        fields = [(k, v) for k, v in clean_row.items() if k not in ("text", "source")]

    return {
        "number": number,
        "source": source,
        "badges": badges,
        "image_html": img,
        "image_ok": ok,
        "ocr_text": ocr_row.get("text", ""),
        "fields": fields,
    }


def show_pipeline(args: argparse.Namespace) -> None:
    """Match OCR and cleaned records by source and write a single-file HTML report."""
    job_began = log.job_began(args.log_file, args=args)

    ocr_records = pd.read_csv(args.ocr_file, dtype=str).fillna("").to_dict("records")
    clean_records = (
        pd.read_csv(args.clean_file, dtype=str).fillna("").to_dict("records")
    )
    clean_by_source: dict[str, dict] = {}
    for row in clean_records:
        clean_by_source.setdefault(row["source"], row)

    rows = ocr_records[: args.limit]

    cards = []
    ocr_errors = 0
    missing_clean = 0
    missing_image = 0
    for number, ocr_row in enumerate(rows, 1):
        clean_row = clean_by_source.get(ocr_row["source"])
        card = build_card(number, ocr_row, clean_row)
        cards.append(card)
        status = ocr_row.get("status", "").strip().lower()
        if status != "success":
            ocr_errors += 1
        if clean_row is None:
            missing_clean += 1
        if not card["image_ok"]:
            missing_image += 1

    css = (TEMPLATES_DIR / "show_pipeline.css").read_text(encoding="utf-8")
    html_doc = load_template().render(
        css=css,
        generated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ocr_file=str(args.ocr_file),
        clean_file=str(args.clean_file),
        total_ocr=len(ocr_records),
        shown=len(cards),
        limit=args.limit,
        ocr_errors=ocr_errors,
        missing_clean=missing_clean,
        missing_image=missing_image,
        cards=cards,
    )

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(html_doc, encoding="utf-8")

    size_mb = args.output_file.stat().st_size / (1024 * 1024)
    logging.info(
        f"Report with {len(cards)} records written to "
        f"{args.output_file} ({size_mb:.1f} MB)"
    )
    log.job_elapsed(job_began)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Show the progress of the labeling pipeline (image, OCRed text, and
                final cleaned data) as a single self-contained HTML page. Images are
                embedded as base-64 so the file can be opened and shared on its
                own."""
        ),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--ocr-file",
        type=Path,
        required=True,
        metavar="path",
        help="""CSV file with the OCRed data. It must have 'source' and 'text'
            columns. The 'source' column holds the link/path to the image.""",
    )
    io_group.add_argument(
        "--clean-file",
        type=Path,
        required=True,
        metavar="path",
        help="""CSV file with the final cleaned data. Records are matched to the
            OCR file via their 'source' columns.""",
    )
    io_group.add_argument(
        "--output-file",
        type=Path,
        required=True,
        metavar="path",
        help="""Write the single-file HTML report to this path.""",
    )
    logging_group = arg_parser.add_argument_group("logging options")
    logging_group.add_argument(
        "--log-file",
        type=Path,
        metavar="string",
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    logging_group.add_argument(
        "--notes",
        metavar="string",
        help="""Notes for logging. They only appear in the log file.""",
    )
    debugging_group = arg_parser.add_argument_group("debugging options")
    debugging_group.add_argument(
        "--limit",
        type=int,
        default=5,
        metavar="int",
        help="""Limit the report to this many records. (default: %(default)s)
            The full report can be very large because every image is embedded.""",
    )
    ns = arg_parser.parse_args(args)
    if not ns.ocr_file.is_file():
        arg_parser.error(f"--ocr-file is not a file: {ns.ocr_file}")
    if not ns.clean_file.is_file():
        arg_parser.error(f"--clean-file is not a file: {ns.clean_file}")
    if ns.limit < 1:
        arg_parser.error("--limit must be >= 1")
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    show_pipeline(ARGS)
