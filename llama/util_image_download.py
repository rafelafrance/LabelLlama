#!/usr/bin/env python3

import argparse
import logging
import socket
import textwrap
import warnings
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path

import pandas as pd
import PIL
import requests
from PIL import Image
from tqdm import tqdm

from llama.pylib import log

TIMEOUT = 12  # Seconds to wait for a server reply
DELAY = 2  # Seconds to delay between attempts to download an image

Image.MAX_IMAGE_PIXELS = 300_000_000

TOO_DAMN_SMALL = 10_000
TOO_BIG = 32_000_000


IMAGE_ERRORS = (
    AttributeError,
    BufferError,
    ConnectionError,
    EOFError,
    FileNotFoundError,
    IOError,
    Image.DecompressionBombError,
    Image.UnidentifiedImageError,
    IndexError,
    OSError,
    RuntimeError,
    SyntaxError,
    TimeoutError,
    TypeError,
    ValueError,
    requests.exceptions.ReadTimeout,
    PIL.UnidentifiedImageError,
)
# Set a timeout for requests
socket.setdefaulttimeout(TIMEOUT)


def main(args: argparse.Namespace) -> None:
    log.started(args=args)

    args.image_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(
        args.multimedia_tsv,
        sep="\t",
        usecols=["gbifID", "format", "identifier", "title"],
    )
    rows = df.to_dict("records")
    rows = rows[args.offset : args.offset + args.limit]

    with tqdm(total=len(rows)) as pbar:
        results = []
        counts = defaultdict(int)

        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(download, row, args.image_dir) for row in rows]
            for future in as_completed(futures):
                results.append(future.result())
                pbar.update(1)

    for result in results:
        counts[result] += 1

    logging.info(
        f"Total {len(rows)} downloads: {counts['download']} "
        f"exists {counts['exists']} errors {counts['error']}"
    )

    log.finished()


def download(row: dict, image_dir: Path) -> str:
    title = row["title"].replace(" ", "_")
    suffix = row["format"].rsplit("/", maxsplit=1)[-1]
    path: Path = image_dir / f"{row['gbifID']}_{title}.{suffix}"

    if path.exists():
        return "exists"

    try:
        data = requests.get(row["identifier"], timeout=TIMEOUT).content

    except requests.exceptions.RequestException:
        logging.exception("Download error")
        return "error"

    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings

            with Image.open(BytesIO(data)) as image:
                image.save(path)
            # with path.open("wb") as f:
            #     f.write(data)

    except IMAGE_ERRORS:
        logging.exception("Download error")
        return "error"

    return "download"


def log_counts(counts: dict[str, int]) -> None:
    for key, value in counts.items():
        msg = f"Count {key} = {value}"
        logging.info(msg)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""Download images."""),
    )
    arg_parser.add_argument(
        "--multimedia-tsv",
        type=Path,
        required=True,
        metavar="PATH",
        help="""This TSV file is holding download links.""",
    )
    arg_parser.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Place downloaded images into this directory.""",
    )
    arg_parser.add_argument(
        "--offset",
        type=int,
        default=0,
        metavar="INT",
        help="""Offset into the multimedia file. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--limit",
        type=int,
        default=400,
        metavar="INT",
        help="""Limit to this many downloads attempts. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--threads",
        type=int,
        default=1,
        metavar="INT",
        help="""How many worker threads to spawn. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        metavar="path",
        help="""Append logging notices to this file. It also logs the script options
            so you may use this to keep track of what you did.""",
    )
    arg_parser.add_argument(
        "--notes",
        metavar="string",
        help="""Notes for logging. They only appear in the log file.""",
    )
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
