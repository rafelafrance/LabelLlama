#!/usr/bin/env python3

import argparse
import textwrap
from datetime import datetime
from pathlib import Path

import duckdb
import lmstudio as lms
import polars as pl
from tqdm import tqdm

from llama.common import db_util

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


def ocr_action(args: argparse.Namespace) -> None:
    """OCR images in a directory."""
    with lms.Client(args.api_host) as client, duckdb.connect(args.db) as cxn:
        image_paths = filter_images(args)

        job_id, job_started = db_util.add_job(
            cxn, __file__, args=args, params={"prompt": PROMPT}
        )

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

            doc_text, doc_error = "", ""
            try:
                doc_text = model.respond(chat)
            except lms.LMStudioServerError as err:
                doc_error = f"Server error: {err}"

            cxn.execute(
                """
                insert into docs (job_id, src_path, doc_text, doc_error, doc_elapsed)
                values (?, ?, ?, ?, ?);
                """,
                [
                    job_id,
                    str(image_path),
                    str(doc_text),
                    doc_error,
                    str(datetime.now() - rec_began),
                ],
            )

        db_util.update_elapsed(cxn, job_id, job_started)


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
        description=textwrap.dedent("""OCR images."""),
    )
    subparsers = arg_parser.add_subparsers(
        title="Subcommands",
        description="Actions on gold standard records",
        dest="action",
    )

    # ------------------------------------------------------------
    ocr_parser = subparsers.add_parser(
        "ocr",
        help="""OCR images.""",
    )
    ocr_parser.add_argument(
        "--spreadsheet",
        type=Path,
        help="""Path to the ODS spreadsheet.""",
    )
    ocr_parser.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        help="""Directory containing all of the images to OCR.""",
    )
    ocr_parser.add_argument(
        "--model",
        default="noctrex/Chandra-OCR-GGUF/Chandra-OCR-Q4_K_S.gguf",
        help="""Use this language model. (default: %(default)s)""",
    )
    ocr_parser.add_argument(
        "--api-host",
        default="http://localhost:1234",
        help="""URL for the language model. (default: %(default)s)""",
    )
    ocr_parser.add_argument(
        "--context-length",
        type=int,
        default=4096,
        help="""Model's context length. (default: %(default)s)""",
    )
    ocr_parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="""Model's temperature. (default: %(default)s)""",
    )
    ocr_parser.add_argument(
        "--notes",
        default="",
        help="""Notes about this dataset.""",
    )
    ocr_parser.add_argument(
        "--missing",
        action="store_true",
        help="""Process all images in image dir but not in the database.
            Use this when you want to restart a job after is crashes.""",
    )
    ocr_parser.add_argument(
        "--retry",
        action="store_true",
        help="""Retry all images where all previous attempts errored out.
            Use this to try the OCR with a different model and/or parameters.""",
    )
    ocr_parser.set_defaults(func=ocr_action)

    # ------------------------------------------------------------
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    ARGS.func(ARGS)
