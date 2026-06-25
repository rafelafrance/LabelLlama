#!/usr/bin/env python3

import argparse
import json
import os
import textwrap
from pathlib import Path
from pprint import pp

from dotenv import load_dotenv
from pygbif import collection, institution, occurrences

from llama.pylib import log

TARGET_INSTITUTIONS = """
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

KINGDOM_KEY = 6
BATCH_SIZE = 100


def get_gbif(args: argparse.Namespace) -> None:
    log.started(args=args)

    user = os.getenv("GBIF_USER")
    pwd = os.getenv("GBIF_PWD")

    inst_code = args.institution_code or get_institution_code(
        args.institution, user, pwd
    )

    occur = {}

    # Read previous data
    if args.gbif_json.exists():
        with args.gbif_json.open() as jin:
            rows = json.load(jin)
        occur = {r["gbifID"]: r for r in rows if r.get("kingdomKey") == KINGDOM_KEY}

    # Get more data
    for offset in range(args.offset, args.offset + args.limit, BATCH_SIZE):
        results = occurrences.search(
            institutionCode=inst_code,
            basisOfRecord="PRESERVED_SPECIMEN",
            kingdomKey=KINGDOM_KEY,
            mediatype="StillImage",
            limit=BATCH_SIZE,
            offset=offset,
            user=user,
            pwd=pwd,
        )
        # Append new records
        occur |= {
            r["gbifID"]: r
            for r in results["results"]
            if r.get("taxonRank") in ("SPECIES", "SUBSPECIES", "VARIETY")
        }
        print(f"{len(occur)=}")

        # Early stopping
        if len(results["results"]) < BATCH_SIZE or len(occur) >= args.limit:
            break

    with args.gbif_json.open("w") as jfile:
        json.dump(list(occur.values()), jfile, indent=4)

    log.finished()


def get_occurrences(
    inst_code: str, limit: int, user: str | None, pwd: str | None
) -> list[dict]:
    results = occurrences.search(
        institutionCode=inst_code,
        basisOfRecord="PRESERVED_SPECIMEN",
        mediatype="StillImage",
        kingdomKey=KINGDOM_KEY,
        limit=limit,
        user=user,
        pwd=pwd,
    )
    return results["results"]


def get_collection(inst_code: str, user: str | None, pwd: str | None) -> dict:
    results = collection.search(code=inst_code, user=user, pwd=pwd)
    for result in results["results"]:
        pp(result)
    return {}


def get_institution_code(institute: str, user: str | None, pwd: str | None) -> str:
    results = institution.search(q=institute, user=user, pwd=pwd)
    max_count = -1, ""
    for result in results["results"]:
        # pp(result)
        # print()
        if "institutionCode" not in result:
            continue
        count = int(result["occurrenceCount"]), result.get("institutionCode")
        max_count = max(max_count, count)
    return max_count[1]


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Get data from GBIF using their API."""),
    )
    arg_parser.add_argument(
        "--institution",
        help="""Search for the institution code with this string.""",
    )
    arg_parser.add_argument(
        "--institution-code",
        help="""You know the institution code.""",
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
    arg_parser.add_argument(
        "--offset",
        type=int,
        default=0,
        metavar="int",
        help="""Start getting records from this offset.""",
    )
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    load_dotenv()
    ARGS = parse_args()
    get_gbif(ARGS)
