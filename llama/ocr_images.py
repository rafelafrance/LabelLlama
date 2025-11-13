#!/usr/bin/env python3

import argparse
import io
import json
import textwrap
from datetime import datetime
from pathlib import Path

import lmstudio as lms
from rich.console import Console

PROMPT = " ".join(
    """
    You are given an image of a museum specimen with labels.
    I want you to extract all of the text from every label on the specimen.
    This includes text from both typewritten and handwritten labels.
    Do not get confused by the specimen itself which is in the center of the image.
    Do not hallucinate.
    """.split()
)


def main(args: argparse.Namespace) -> None:
    console = Console(log_path=False)
    console.log("[blue]Started")
    job_started = datetime.now()

    image_paths = sorted(args.image_dir.glob("*.jpg"))
    image_paths = image_paths[args.first : args.last]
    start = args.first if args.first else 0

    with lms.Client(args.api_host) as client, args.ocr_jsonl.open("a") as out_file:
        model = client.llm.model(args.model_name)

        for i, image_path in enumerate(image_paths, start):
            rec_start = datetime.now()
            console.log(f"[blue]{'=' * 80}")
            console.log(f"[blue]{i} {image_path}")

            handle = client.files.prepare_image(image_path)
            chat = lms.Chat()
            chat.add_user_message(PROMPT, images=[handle])

            try:
                ocr_text = model.respond(chat)
            except lms.LMStudioServerError as err:
                ocr_error = f"Server error: {err}"
                append_result(out_file, args.model_name, image_path, ocr_error, "")
                console.log(f"[red]{ocr_error}")
                continue

            result = append_result(
                out_file, args.model_name, image_path, "", str(ocr_text)
            )
            console.log(f"[green]{result['ocr_text']}")
            console.log(f"[blue]Inference Time: {datetime.now() - rec_start}")

    console.log(f"[blue]Job Time: {datetime.now() - job_started}")
    console.log("[blue]Finished")


def append_result(
    out_file: io.StringIO,
    model_name: str,
    image_path: Path,
    ocr_error: str,
    ocr_text: str,
) -> dict:
    result = {
        "image_path": str(image_path),
        "ocr_model": model_name,
        "ocr_error": ocr_error,
        "ocr_time": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "ocr_text": ocr_text,
    }
    out_file.write(json.dumps(result))
    out_file.write("\n")
    out_file.flush()

    return result


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""
            OCR a directory full of museum specimen images.
            """),
    )

    arg_parser.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Images of museum specimens are in this directory.""",
    )

    arg_parser.add_argument(
        "--ocr-jsonl",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output OCRed text to this JSONL file.""",
    )

    arg_parser.add_argument(
        "--model-name",
        default="noctrex/Chandra-OCR-GGUF",
        help="""Use this language model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--api-host",
        default="localhost:1234",
        help="""URL for the LM model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--first",
        type=int,
        metavar="INT",
        help="""The index of the first image to process.""",
    )

    arg_parser.add_argument(
        "--last",
        type=int,
        metavar="INT",
        help="""The index of the last image to process.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
