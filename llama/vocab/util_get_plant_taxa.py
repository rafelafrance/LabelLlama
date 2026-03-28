#!/usr/bin/env python3
"""
Build taxon terms from downloaded data.

1. ITIS sqlite database: www.itis.gov/downloads/index.html
2. Plant of the World Online: sftp.kew.org/pub/data-repositories/WCVP/
"""

import argparse
import csv
import sqlite3
import textwrap
from pathlib import Path

from llama.common import log

ITIS_SPECIES_ID = 220


def get_taxa(args: argparse.Namespace) -> None:
    log.started(args.log_file, args=args)

    taxa = {}
    taxa |= read_wcvp_taxa(args.wcvp_file)
    taxa |= read_itis_taxa(args.itis_db)

    taxa = dict(sorted(taxa.items()))

    write_csv(taxa)

    log.finished()


def write_csv(taxa: dict[str, str]) -> None:
    path = Path(__file__).parent / "terms" / "genus_to_family.csv"

    with path.open("w") as out:
        writer = csv.writer(out)
        writer.writerow(["genus", "family"])
        for genus, family in taxa.items():
            writer.writerow([genus, family])


def read_wcvp_taxa(wcvp_file: Path) -> dict[str, str]:
    taxa = {}
    with wcvp_file.open() as in_file:
        reader = csv.DictReader(in_file, delimiter="|")
        for row in reader:
            taxa[row["genus"]] = row["family"]
    return taxa


def read_itis_taxa(itis_db: Path) -> dict[str, str]:
    taxa = {}

    kingdom_id, family_id, genus_id = 3, 140, 180

    genus_sql = """
        select complete_name, hierarchy_string
          from hierarchy join taxonomic_units using (tsn)
         where kingdom_id = ? and rank_id = ?
        """
    family_sql = """
        select complete_name, tsn
          from taxonomic_units
         where kingdom_id = ? and rank_id = ?
        """
    with sqlite3.connect(itis_db) as cxn:
        cxn.row_factory = sqlite3.Row
        families = cxn.execute(family_sql, (kingdom_id, family_id)).fetchall()
        families = {f["tsn"]: f["complete_name"] for f in families}
        genera = cxn.execute(genus_sql, (kingdom_id, genus_id)).fetchall()
        genera = [dict(g) for g in genera]

        for genus in genera:
            for tsn in genus["hierarchy_string"].split("-"):
                tsn = int(tsn)
                if tsn in families:
                    taxa[genus["complete_name"]] = families[tsn]
                    break

    return taxa


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Get plant family and genus names."""),
    )
    arg_parser.add_argument(
        "--itis-db",
        type=Path,
        metavar="PATH",
        help="""Get terms from this ITIS database.""",
    )

    arg_parser.add_argument(
        "--wcvp-file",
        type=Path,
        metavar="PATH",
        help="""Get terms from this WCVP file. It is a '|' separated CSV.""",
    )
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    get_taxa(ARGS)
