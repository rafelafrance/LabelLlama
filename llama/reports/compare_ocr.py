#!/usr/bin/env python3

import argparse
import glob as globmod
import logging
import textwrap
from dataclasses import dataclass
from pathlib import Path

import jinja2
import pandas as pd
from tqdm import tqdm

from llama.pylib import image_util, log
from llama.results.model_status import ModelStatus

TEMPLATES_DIR = Path(__file__).parent / "templates"

REQUIRED_COLUMNS = {"source", "text"}


@dataclass
class OcrResult:
    """The latest successful OCR result for one source from one run file."""

    file: str
    source: str
    status: str
    elapsed: str
    text: str


@dataclass
class SourceGroup:
    """All model runs for a single source image."""

    source: str
    results: dict[str, OcrResult]  # keyed by file stem, in CLI order
    image: str | None = None  # data: URI, None if unavailable


def load_latest_success(ocr_file: Path) -> dict[str, OcrResult]:
    """Load one CSV, keeping the last successful row per source."""
    df = pd.read_csv(ocr_file, dtype=str).fillna("")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        missing_str = ", ".join(sorted(missing))
        raise ValueError(
            f"OCR file {ocr_file} is missing required columns: {missing_str}"
        )

    latest: dict[str, OcrResult] = {}
    for row in df.to_dict("records"):
        if not ModelStatus.is_success(row.get("status", "")):
            continue
        latest[row["source"]] = OcrResult(
            file=ocr_file.stem,
            source=row["source"],
            status=row.get("status", ""),
            elapsed=row.get("elapsed", ""),
            text=row["text"],
        )
    return latest


def expand_ocr_files(patterns: list[str]) -> list[Path]:
    """Expand each glob pattern to its matching files, in order."""
    ocr_files: list[Path] = []
    for pattern in patterns:
        matches = sorted(globmod.glob(pattern))
        if not matches:
            raise ValueError(f"No files match OCR file pattern: {pattern}")
        ocr_files.extend(Path(match) for match in matches)
    return list(dict.fromkeys(ocr_files))


def build_groups(files: list[Path]) -> tuple[list[str], list[SourceGroup]]:
    """Group latest successful results by source for sources in every file."""
    per_file = [load_latest_success(f) for f in files]
    stems = [f.stem for f in files]

    common = set(per_file[0])
    for per in per_file[1:]:
        common &= set(per)

    groups = []
    for source in sorted(common):
        results = {stem: per[source] for stem, per in zip(stems, per_file, strict=True)}
        groups.append(SourceGroup(source=source, results=results))
    return stems, groups


def attach_images(groups: list[SourceGroup]) -> None:
    """Fill in base-64 thumbnails for each group's source image."""
    for group in tqdm(groups, desc="Embedding images"):
        try:
            base64_image, mime_type = image_util.downscale(group.source)
        except image_util.IMAGE_ERRORS:
            logging.warning(f"Image unavailable: {group.source}")
            continue
        group.image = f"data:{mime_type};base64,{base64_image}"


def load_template() -> jinja2.Template:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
        autoescape=True,
    )
    return env.get_template("compare_ocr.html")


def render_html(stems: list[str], groups: list[SourceGroup]) -> str:
    css = (TEMPLATES_DIR / "compare_ocr.css").read_text(encoding="utf-8")
    js = (TEMPLATES_DIR / "compare_ocr.js").read_text(encoding="utf-8")
    return load_template().render(
        css=css,
        js=js,
        engines=stems,
        stems=stems,
        groups=groups,
    )


def compare(args: argparse.Namespace) -> None:
    """Group OCR results by source and write an HTML comparison report."""
    job_began = log.job_began(None, args=args)

    stems, groups = build_groups(expand_ocr_files(args.ocr_file))
    attach_images(groups)
    args.html_out.write_text(render_html(stems, groups))

    print(f"{len(groups)} sources written to {args.html_out}")
    log.job_elapsed(job_began)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Compare OCR results from different models."""),
    )
    arg_parser.add_argument(
        "--ocr-file",
        type=str,
        required=True,
        action="append",
        metavar="glob",
        help="""OCR results CSV for one model run, or a glob pattern matching
            several. Pass this flag once per model (or pattern).""",
    )
    arg_parser.add_argument(
        "--html-out",
        type=Path,
        required=True,
        metavar="path",
        help="""Path of the HTML report to write.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    compare(ARGS)
