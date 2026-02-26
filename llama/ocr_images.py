#!/usr/bin/env python3
"""OCR a directory of images."""

import argparse
import textwrap
from datetime import datetime
from pathlib import Path

import duckdb
import lmstudio as lms
import polars as pl
from tqdm import tqdm

from llama.pylib.db_util import create_ocr_tables

# A reasonable starting prompt. I will parameterize and try variations on this later.
PROMPT = " ".join(
    """
    You are given an image of a museum specimen with labels.
    I want you to extract all of the text from every label on the specimen.
    This includes text from both typewritten and handwritten labels.
    Do not get confused by the specimen itself which is in the center of the image.
    I want plain text without HTML or markdown tags.
    Do not hallucinate.
    """.split()
)


def ocr_images(args: argparse.Namespace) -> None:
    """OCR all images in the directory."""
    create_ocr_tables(args.db_path)

    job_began = datetime.now()

    with lms.Client(args.api_host) as client, duckdb.connect(args.db) as cxn:
        image_paths = filter_images(args)

        run_id = cxn.execute(
            """
            insert into ocr_run
                (prompt, model, api_host, notes, temperature, context_length)
                values (?, ?, ?, ?, ?, ?)
                returning ocr_run_id;
            """,
            [
                PROMPT,
                args.model_name,
                args.api_host,
                args.notes.strip(),
                args.temperature,
                args.context_length,
            ],
        ).fetchone()
        if not run_id:
            raise ValueError(f"Could not find the given ocr-run-id {args.ocr_run_id}")
        run_id = run_id[0]

        model = client.llm.model(
            args.model_name,
            config={
                "temperature": args.temperature,
                "contextLength": args.context_length,
            },
        )

        for image_path in tqdm(image_paths):
            rec_began = datetime.now()

            handle = client.files.prepare_image(image_path)
            chat = lms.Chat()
            chat.add_user_message(PROMPT, images=[handle])

            ocr_text, ocr_error = "", ""
            try:
                ocr_text = model.respond(chat)
            except lms.LMStudioServerError as err:
                ocr_error = f"Server error: {err}"

            cxn.execute(
                """
                insert into ocr
                    (ocr_run_id, image_path, ocr_text, ocr_error, elapsed)
                    values (?, ?, ?, ?, ?);
                """,
                [
                    run_id,
                    str(image_path),
                    str(ocr_text),
                    ocr_error,
                    datetime.now() - rec_began,
                ],
            )

        job_elapsed = datetime.now() - job_began
        cxn.execute(
            "update ocr_run set elapsed = ? where ocr_run_id = ?;",
            [job_elapsed, run_id],
        )


def get_all_records(db_path: Path) -> pl.DataFrame:
    with duckdb.connect(db_path) as cxn:
        return cxn.execute("select * from ocr;").pl()


def get_all_images(db_path: Path) -> pl.DataFrame:
    """Get all image paths in the database."""
    with duckdb.connect(db_path) as cxn:
        all_images = cxn.execute("select distinct image_path from ocr;").pl()
    return all_images


def get_all_errors(db_path: Path) -> pl.DataFrame:
    """
    Get records that only have errors. I.e. not successfully OCRed even once.
    Note that errors do not go away they are "overwritten" by later successful OCR
    attempts,typically with changed model parameters or a different model.
    """
    sql = """
        select image_path, max(ocr_text) as top
            from ocr
            group by image_path
            having top = '';
        """
    with duckdb.connect(db_path) as cxn:
        return cxn.execute(sql).pl()


def filter_images(args: argparse.Namespace) -> list[Path]:
    """
    Filter images.

    - Missing images. The job crashed, and you want all remaining images using the
      --missing flag.
    - The --retry flag only selects images that have never successfully OCRed, i.e.
      they always errored out. I use this to try a different model and/or parameters
      on the problem images.
    """
    image_paths = sorted(args.image_dir.glob("*.jpg"))

    # Only get --missing image paths, images not already in the DB
    if args.missing:
        completed = {r[0] for r in get_all_images(args.db).rows()}
        image_paths = [p for p in image_paths if str(p) not in completed]

    # Get images to --retry, images with only errors
    if args.retry:
        errored = {r[0] for r in get_all_errors(args.db).rows()}
        image_paths = [p for p in image_paths if str(p) in errored]

    return image_paths


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""OCR all images in a directory."""),
    )

    arg_parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the database.""",
    )

    arg_parser.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Directory containing all of the images to OCR.""",
    )

    arg_parser.add_argument(
        "--model",
        default="noctrex/Chandra-OCR-GGUF/Chandra-OCR-Q4_K_S.gguf",
        help="""Use this language model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--api-host",
        default="http://localhost:1234",
        help="""URL for the language model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--context-length",
        type=int,
        default=4096,
        help="""Model's context length. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="""Model's temperature. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        help="""Notes about this dataset.""",
    )

    arg_parser.add_argument(
        "--missing",
        action="store_true",
        help="""Process all images in image dir but not in the database.""",
    )

    arg_parser.add_argument(
        "--retry",
        action="store_true",
        help="""Retry all images where all previous attempts errored out.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    ocr_images(ARGS)
