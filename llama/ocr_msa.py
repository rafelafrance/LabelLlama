#!/usr/bin/env python3

import argparse
import glob
import logging
import textwrap
from collections import defaultdict
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from llama.line_align import char_sub_matrix, label_builder
from llama.line_align.align import LineAlign
from llama.prompts.prompt import REQUIRED_COLUMNS
from llama.pylib import log
from llama.results.doc_utils import read_results_csv
from llama.results.model_status import ModelStatus


def msa_ocr_results(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    # Normalize the list of OCR files
    ocr_files: dict[Path, None] = {}
    for ocr_glob in args.ocr_file:
        matches = sorted(glob.glob(str(ocr_glob), recursive=True))

        if not matches:
            msg = f"No OCR files match the pattern: {ocr_glob}"
            logging.error(msg)
            log.job_elapsed(job_began)
            raise SystemExit(1)

        for match in matches:
            path = Path(match).resolve()
            if not path.is_file():
                logging.warning("Not an OCR file, skipped: %s", path)
                continue
            ocr_files[path] = None

    # Read in the OCR results
    all_ocr = defaultdict(list)
    skipped: list[str] = []

    for ocr_file in ocr_files:
        if ocr_file == args.consensus_file.resolve():
            msg = f"Not using the consensus file as input: {ocr_file}"
            logging.error(msg)
            log.job_elapsed(job_began)
            raise SystemExit(1)

        try:
            df = read_results_csv(ocr_file, "OCR file")
        except ValueError as err:
            # One damaged file must not lose us the rest of the alignment.
            logging.warning(f"{err}, skipped")
            skipped.append(str(ocr_file))
            continue
        if df is None:
            logging.warning(f"Empty OCR file, skipped: {ocr_file}")
            continue

        if missing := set(REQUIRED_COLUMNS) - set(df.columns):
            logging.warning(
                f"{ocr_file} is not an OCR file (missing "
                f"{', '.join(sorted(missing))}), skipped"
            )
            skipped.append(str(ocr_file))
            continue

        latest: dict[str, str] = {}
        for row in df.to_dict("records"):
            if not ModelStatus.is_success(row["status"]):
                continue
            if not (source := row["source"].strip()):
                logging.warning(f"{ocr_file}: a row has no source, skipped")
                continue
            if text := row["text"].strip():
                latest[source] = text

        for source, text in latest.items():
            all_ocr[source].append(text)

    if skipped:
        logging.warning(f"Skipped {len(skipped)} file(s): {', '.join(skipped)}")

    if not all_ocr:
        files = ", ".join(str(p) for p in ocr_files)
        msg = f"There were no successful OCR rows in: {files}"
        logging.error(msg)
        log.job_elapsed(job_began)
        raise SystemExit(1)

    # Make sure we have the correct characters in the substitution matrix
    chars = set()
    for group in all_ocr.values():
        for ocr in group:
            chars |= set(ocr)
    missing = char_sub_matrix.missing_chars("".join(sorted(chars)))
    if char_sub_matrix.GAP_CHAR in missing:
        msg = (
            f"OCR text contains the gap character {char_sub_matrix.GAP_CHAR!r}, "
            "which is reserved for the alignment. Find it with: "
            "grep -l '⋄' <your OCR CSVs>"
        )
        logging.error(msg)
        log.job_elapsed(job_began)
        raise SystemExit(1)
    if missing:
        missing_str = "".join(missing)
        msg = (
            f"Missing characters not in substitution matrix {missing_str}\n"
            f"Add them with: build_char_sub_matrix.py --chars '{missing_str}'"
        )
        logging.error(msg)
        log.job_elapsed(job_began)
        raise SystemExit(1)

    # Align the OCR results and get a consensus record
    consensus = {}
    subs = char_sub_matrix.get()
    line = LineAlign(subs)
    for source, ocrs in tqdm(all_ocr.items()):
        aligned = line.align(ocrs)
        consensus[source] = label_builder.find_consensus(aligned)

    # Output consensus
    rows = [
        {"status": ModelStatus.SUCCESS, "source": k, "elapsed": "", "text": v}
        for k, v in consensus.items()
    ]
    df = pd.DataFrame(rows, columns=REQUIRED_COLUMNS)
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
    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    log.run_job(msa_ocr_results, ARGS)
