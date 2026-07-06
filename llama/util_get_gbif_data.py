#!/usr/bin/env python3

import argparse
import csv
import logging
import sys
import textwrap
from pathlib import Path

import pandas as pd

from llama.pylib import log

csv.field_size_limit(sys.maxsize)


def get_gbif(args: argparse.Namespace) -> None:
    log.started(args=args)

    logging.info("Building stems")
    gbif_ids = {p.stem: str(p) for p in args.image_dir.glob("*")}
    logging.info(f"{len(gbif_ids)=}")

    logging.info("Building media")
    media_by_gbif = {}
    with args.multimedia_tsv.open() as fin:
        reader = csv.DictReader(fin, delimiter="\t")
        for row in reader:
            media_by_gbif[row["gbifID"]] = row
    logging.info(f"{len(media_by_gbif)=}")

    logging.info("Building occur")
    occur_by_gbif = {}
    with args.occurrence_tsv.open() as fin:
        reader = csv.DictReader(fin, delimiter="\t")
        for row in reader:
            occur_by_gbif[row["gbifID"]] = row
    logging.info(f"{len(occur_by_gbif)=}")

    logging.info("Building gbif")
    gbif = []
    missing = 0
    for gbif_id, path in gbif_ids.items():
        if gbif_id in media_by_gbif and gbif_id in occur_by_gbif:
            media = media_by_gbif[gbif_id]
            gbif.append(
                {
                    "source": path,
                    "identifier": media["identifier"],
                    **occur_by_gbif[media["gbifID"]],
                }
            )
        else:
            logging.info(f"{gbif_id=}")
            missing += 1

    logging.info(f"{len(gbif)=}")
    logging.info(f"{missing=}")

    df = pd.DataFrame(gbif)
    df.to_csv(args.gbif_file, index=False)

    log.finished()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""
            Get original GBIF info for the images.

            I'm limiting the larger GBIF dumps to the images that were downloaded.
            """),
    )

    arg_parser.add_argument(
        "--image-dir",
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
