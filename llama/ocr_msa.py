#!/usr/bin/env python3

import argparse
import textwrap
from collections import defaultdict
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from llama.line_align import char_sub_matrix, label_builder
from llama.line_align.align import LineAlign
from llama.prompts.prompt import FIRST_COLUMNS
from llama.pylib import log
from llama.results.model_status import ModelStatus


def msa_ocr_results(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    # Read in the OCR results
    all_ocr = defaultdict(list)

    for ocr_glob in args.ocr_file:
        for ocr_file in Path().glob(ocr_glob):
            df = pd.read_csv(ocr_file)
            if missing := set(FIRST_COLUMNS) - set(df.columns):
                raise ValueError(f"{ocr_file} is missing {', '.join(missing)}")
            for row in df.to_dict("records"):
                if ModelStatus.is_success(row["status"]):
                    all_ocr[row["source"]].append(row["text"])

    # Align the OCR results and get a consensus record
    consensus = {}
    subs = char_sub_matrix.get()
    line = LineAlign(subs)
    for source, ocrs in tqdm(all_ocr.items()):
        aligned = line.align(ocrs)
        consensus[source] = label_builder.find_consensus(aligned)

    # Output consensus
    rows = [{"source": k, "text": v} for k, v in consensus.items()]
    df = pd.DataFrame(rows)
    args.consensus_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.consensus_file, index=False)

    log.job_elapsed(job_began)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Do a multiple sequence alignment on OCR results.

            Handwritten (and other) labels do not always OCR well. This program will
            combine an OCRed file from multiple OCR runs, typically with different
            models, into a single Multiple Sequence Alignment (MSA). I then take the
            consensus sequence of the MSA. The hope is that the consensus sequence is
            better than the best OCR result.

            For example:

            That is if I am given a set of strings like:
                MOJAVE DESERT, PROVIDENCE MTS.: canyon above
                E. MOJAVE DESERT , PROVIDENCE MTS . : canyon above
                E MOJAVE DESERT PROVTDENCE MTS. # canyon above
                Be ‘MOJAVE DESERT, PROVIDENCE canyon “above

            I should get back something similar to the following. The exact return value
            will depend on the substitution matrix, gap, and skew penalties passed to
            the function.

                ⋄⋄⋄⋄MOJAVE DESERT, PROVIDENCE MTS.: canyon ⋄above
                E.⋄ MOJAVE DESERT, PROVIDENCE MTS.: canyon ⋄above
                E⋄⋄ MOJAVE DESERT⋄ PROVTDENCE MTS.# canyon ⋄above
                Be ‘MOJAVE DESERT, PROVIDENCE ⋄⋄⋄⋄⋄⋄canyon “above

            Where "⋄" characters are used to represent gaps in the alignments. Gaps do
            not appear in the consensus sequence.

            The consensus sequence is (depending on alignment & consensus parameters):

                E MOJAVE DESERT, PROVIDENCE MTS.: canyon above

            Note that alignments are based on a rough estimate of character similarity.
            """,
        ),
    )
    io_group = arg_parser.add_argument_group("I/O options")
    io_group.add_argument(
        "--ocr-file",
        type=Path,
        required=True,
        action="append",
        metavar="path",
        help="""These CSV files contain results from OCR runs. You may use globs.""",
    )
    io_group.add_argument(
        "--consensus-file",
        type=Path,
        required=True,
        metavar="path",
        help="""Write the multiple sequence consensuses to this CSV file.""",
    )
    logging_group = arg_parser.add_argument_group("logging options")
    logging_group.add_argument(
        "--log-file",
        type=Path,
        metavar="path",
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
        metavar="int",
        help="""Limit to this many records.""",
    )
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    msa_ocr_results(ARGS)
