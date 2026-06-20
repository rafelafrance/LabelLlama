#!/usr/bin/env python3

import argparse
import csv
import textwrap
from pathlib import Path

import pandas as pd

from llama.pylib import log


def get_gbif(args: argparse.Namespace) -> None:
    log.started(args=args)

    with args.ocr_file.open() as fin:
        reader = csv.DictReader(fin)
        targets = {
            Path(r["source"]).stem.split("_", maxsplit=1)[0]: r["source"]
            for r in reader
        }

    with args.occurrence_tsv.open() as fin:
        reader = csv.DictReader(fin, delimiter="\t")
        gbif = {
            row["gbifID"]: {"source": source} | row
            for row in reader
            if (source := targets.get(row["gbifID"]))
        }

    with args.multimedia_tsv.open() as fin:
        reader = csv.DictReader(fin, delimiter="\t")
        for row in reader:
            if targets.get(row["gbifID"]):
                gbif_rec = gbif[row["gbifID"]]
                gbif_rec["identifier"] = row["identifier"]

    df = pd.DataFrame(gbif.values())
    df.to_csv(args.gbif_file, index=False)

    log.finished()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Get original GBIF info for the images."""),
    )

    arg_parser.add_argument(
        "--ocr-file",
        type=Path,
        required=True,
        metavar="PATH",
        help="""This is the OCR file that contains the gbifIDs we are targeting.""",
    )

    arg_parser.add_argument(
        "--occurrence-tsv",
        type=Path,
        required=True,
        metavar="PATH",
        help="""This TSV file contains the GBIF data.""",
    )

    arg_parser.add_argument(
        "--multimedia-tsv",
        type=Path,
        required=True,
        metavar="PATH",
        help="""This TSV file contains the image download links.""",
    )

    arg_parser.add_argument(
        "--gbif-file",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output the GBIF data to this file.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    get_gbif(ARGS)
