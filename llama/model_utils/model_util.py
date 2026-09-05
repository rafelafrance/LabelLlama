import logging
from pathlib import Path
from typing import TYPE_CHECKING

from requests.adapters import HTTPAdapter

from llama.model_utils.model_status import ModelStatus

if TYPE_CHECKING:
    import csv
    import io
    from concurrent.futures import Future

    from requests import Session
    from tqdm import tqdm

    from llama.model_utils.model_args import ExtractArgs, OcrArgs, ParserArgs
    from llama.model_utils.ocr_docs import OcrDocs
    from llama.model_utils.parsed_docs import ParsedDocs

DEFAULT_POOL = 10


def init_session_pool(session: Session, threads: int) -> None:
    if threads > DEFAULT_POOL:
        adapter = HTTPAdapter(pool_connections=threads, pool_maxsize=threads)
        session.mount("http://", adapter)
        session.mount("https://", adapter)


def complete_task(
    writer: csv.DictWriter,
    future: Future[dict],
    out_file: io.StringIO,
    statuses: dict,
    progress_bar: tqdm,
) -> None:
    progress_bar.update(1)
    result = future.result()
    try:
        writer.writerow(result)
        statuses[result["status"]] += 1
        out_file.flush()
    except ValueError as err:
        logging.exception(f"Parse error for: {Path(result['source']).name}")
        text = str(err)
        logging.exception(text)
        writer.writerow(
            {
                "status": ModelStatus.ERROR,
                "source": result["source"],
                "text": text,
            }
        )


def add_payload_args(args: ExtractArgs | OcrArgs | ParserArgs, payload: dict) -> None:
    if args.temperature is not None:
        payload["temperature"] = args.temperature
    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens
    if hasattr(args.prompt, "json_schema") and args.prompt.json_schema:
        payload["character_schema"] = args.prompt.json_schema


def log_what_to_do(docs: OcrDocs | ParsedDocs, target: str) -> None:
    logging.info(f"There are {docs.input_len} {target} to process")
    logging.info(f"{len(docs.already_done)} {target} were already done.")
    if docs.limit:
        logging.info(f"Limited to {docs.limit} {target}.")
    logging.info(f"There are {len(docs.tasks)} {target} left to process.")


def log_what_was_done(docs: OcrDocs | ParsedDocs, target: str, statuses: dict) -> None:
    logging.info(
        f"Total {len(docs.tasks)} {target} processed "
        f"with {statuses[ModelStatus.ERROR]} errors "
        f"and {len(docs.already_done)} {target} skipped."
    )
