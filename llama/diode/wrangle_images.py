#!/usr/bin/env python3

"""Put the images into a format that can be used by LabelLlama & HiPerGator."""

import argparse
import io
import logging
import re
import textwrap
import zipfile
from glob import glob
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from llama.pylib import log
from llama.pylib.image_util import IMAGE_ERRORS, TOO_DAMN_SMALL, has_image_suffix

ZIPS = {".zip", ".ZIP"}


def wrangle(args: argparse.Namespace) -> None:
    job_began = log.job_began(args.log_file, args=args)

    image_re = re.compile(args.image_regex, flags=re.IGNORECASE)

    zips = [
        Path(p) for p in glob(args.zip_glob, recursive=True) if Path(p).suffix in ZIPS
    ]
    for zip_path in zips:
        logging.info(f"Extracting from {zip_path}")

        with zipfile.ZipFile(zip_path) as zippy:
            target_paths = [i.filename for i in zippy.infolist()]
            target_paths = [
                p for p in target_paths if image_re.search(p) and has_image_suffix(p)
            ]
            for path in tqdm(target_paths):
                out_file = args.root_dir / path
                if out_file.exists():
                    logging.info(f"Image {out_file} already exists")
                    continue

                out_file.parent.mkdir(parents=True, exist_ok=True)

                data = zippy.read(path, "rb")
                with Image.open(io.BytesIO(data)) as image:
                    try:
                        width, height = image.size
                        resize = False

                        if width * height < TOO_DAMN_SMALL:
                            raise ValueError

                        if image.mode != "RGB":
                            image.convert("RGB")

                        if width < height and args.max_dim < height:
                            width = int(width * (args.max_dim / height))
                            height = args.max_dim
                            resize = True

                        elif args.max_dim < width:
                            height = int(height * (args.max_dim / width))
                            width = args.max_dim
                            resize = True

                        if resize:
                            image = image.resize(
                                (width, height), resample=Image.Resampling.LANCZOS
                            )

                        image.save(out_file)

                    except IMAGE_ERRORS as err:
                        logging.error(f"Error {path}: {str(err)[:120]}")
                        continue

    log.job_elapsed(job_began)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """Use a language model (LM) to extract information directly from
                images, in a single step."""
        ),
    )
    arg_parser.add_argument(
        "--zip-glob",
        metavar="GLOB",
        help="""A glob of all of the zip files containing images. You will need to quote
            this argument. Example '/home/my-name/share/diode/fsca_2611'""",
    )
    arg_parser.add_argument(
        "--image-regex",
        metavar="REGEX",
        help="""Get all image names matching this regex pattern. You will need to quote
            this argument. The regexes are case insensitive. Example: '_card.jpg'""",
    )
    arg_parser.add_argument(
        "--root-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""The root directory for the output images. Images will go into
            subdirectories (gotten from the zip file) of this directory.""",
    )
    arg_parser.add_argument(
        "--max-dim",
        type=int,
        default=2048,
        metavar="INT",
        help="""The maximum edge size in pixels. The other smaller side is be scaled to
            keep the same image ratio. (default: %(default)s)""",
    )
    arg_parser.add_argument(
        "--log-file",
        type=Path,
        metavar="string",
        help="""Append logging notices to this file. It also logs the script arguments
            so you may use this to keep track of what you did.""",
    )
    arg_parser.add_argument(
        "--notes",
        metavar="string",
        help="""Notes for logging. They only appear in the log file.""",
    )

    ns = arg_parser.parse_args(args)
    return ns


if __name__ == "__main__":
    ARGS = parse_args()
    wrangle(ARGS)
