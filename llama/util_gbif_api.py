#!/usr/bin/env python3

import argparse
import json
import os
import textwrap
from pathlib import Path

from dotenv import load_dotenv
from pygbif import institution, occurrences

from llama.pylib import log

"""
New York Botanic Garden
Missouri Botanic Garden
Harvard University Herbarium
Field Museum Herbarium
Jepson Herbarium
California Academy of Science Herbarium
Botanical Research Institute of Texas
University of Wisconsin Herbarium
University of Michigan Herbarium
Cornell University Herbarium
University of Washington Herbarium
"""


def get_gbif(args: argparse.Namespace) -> None:
    log.started(args=args)

    user = os.getenv("GBIF_USER")
    pwd = os.getenv("GBIF_PWD")

    inst_rec = get_institution_code(args.institution, user, pwd)

    occur = []

    for offset in range(0, args.limit, 100):
        results = occurrences.search(
            institutionCode=inst_rec["code"],
            basisOfRecord="PRESERVED_SPECIMEN",
            mediatype="StillImage",
            limit=100,
            offset=offset,
            user=user,
            pwd=pwd,
        )
        occur += results["results"]
        print(f"{len(occur)=}")

    with args.gbif_json.open("w") as jfile:
        json.dump(occur, jfile, indent=4)

    log.finished()


def get_occurrences(
    inst_code: str, limit: int, user: str | None, pwd: str | None
) -> list[dict]:
    results = occurrences.search(
        institutionCode=inst_code,
        basisOfRecord="PRESERVED_SPECIMEN",
        mediatype="StillImage",
        limit=limit,
        user=user,
        pwd=pwd,
    )
    return results["results"]


def get_institution_code(institute: str, user: str | None, pwd: str | None) -> dict:
    results = institution.search(q=institute, user=user, pwd=pwd)
    max_count = -1, {}
    for result in results["results"]:
        count = int(result["occurrenceCount"]), result
        max_count = max(max_count, count)
    return max_count[1]


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Get data from GBIF using their API."""),
    )
    arg_parser.add_argument(
        "--institution",
        required=True,
        help="""Get the institution code.""",
    )
    arg_parser.add_argument(
        "--gbif-json",
        type=Path,
        metavar="path",
        help="""Write the gbif results to this file.""",
    )
    arg_parser.add_argument(
        "--limit",
        type=int,
        default=400,
        metavar="int",
        help="""Limit to this many records.""",
    )
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    load_dotenv()
    ARGS = parse_args()
    get_gbif(ARGS)
