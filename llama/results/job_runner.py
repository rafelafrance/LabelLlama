"""
The threaded work driver shared by ocr_images.py, parse_images.py and parse_text.py.

All three scripts do the same thing: run a model call over a list of tasks in a
thread pool and append one CSV row per task. Keeping the loop in one place means
the resume/exit policy, the CSV header, the HTTP sessions, the progress bar, the
row validation, the error counting and the job trailer cannot drift apart
between scripts.
"""

from __future__ import annotations

import csv
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING

from tqdm import tqdm

from llama.prompts.prompt import REQUIRED_COLUMNS
from llama.pylib import log
from llama.pylib.thread_sessions import ThreadSessions
from llama.results.model_status import ModelStatus, StatusCounts

if TYPE_CHECKING:
    import io
    from collections.abc import Callable, Sequence
    from concurrent.futures import Future
    from datetime import datetime
    from typing import Any

    from llama.prompts.prompt import Prompt

# The image jobs share this: --image-dir is a single directory on purpose, so a
# tree of labels silently yields nothing.
NO_IMAGES_FOUND = (
    "No images found. --image-dir is not recursive; try --image-glob 'dir/**/*.jpg'"
)

MIN_TEXT_LEN = 32


def check_row(result: dict, text: str, prompt: Prompt) -> None:
    """
    Raise ValueError if the model returned no usable output.

    This only applies to prompts with LLM fields beyond the base COLUMNS
    (i.e., parse jobs, not OCR). When text is given and it is shorter
    than MIN_TEXT_LEN the check is skipped, since a small input can
    legitimately yield nothing. When no text is given (e.g., the input
    was an image) the check applies.
    """
    if prompt.req_fields and not all(result.get(req) for req in prompt.req_fields):
        raise ValueError("Missing required field.")

    llm_columns = [c for c in prompt.columns if c not in REQUIRED_COLUMNS]
    if not llm_columns:
        return
    if text and len(text) < MIN_TEXT_LEN:
        return
    if all(not bool(result.get(c, "")) for c in llm_columns):
        raise ValueError("There is no output for this future.")


def future_result(
    future: Future[dict],
    source: Path | str,
    text: str,
    prompt: Prompt,
) -> dict:
    """
    Return the future's result, or an ERROR row if the call raised or the
    result failed check_row.
    """
    try:
        result = future.result()
        if ModelStatus.is_success(result.get("status")):
            check_row(result, text, prompt)
    except Exception as err:
        name = Path(source).name if source else "unknown"
        logging.error(f"Task error for: {name}: {str(err)[:120]}")
        return {
            "status": ModelStatus.ERROR,
            "source": str(source),
            "elapsed": "",
            "text": str(err),
        }
    return result


def write_row(
    writer: csv.DictWriter,
    out_file: io.TextIOBase,
    statuses: StatusCounts,
    result: dict,
    source: Path | str = "",
) -> None:
    """
    Write result as one CSV row, counting its status. A result with a key the
    writer does not know falls back to one ERROR row carrying the writer's
    complaint.
    """
    try:
        writer.writerow(result)
        statuses.count(result.get("status"))
        out_file.flush()
    except ValueError as err:
        name = Path(result["source"]).name
        logging.error(f"Write error for: {name}: {str(err)[:120]}")
        writer.writerow(
            {
                "status": statuses.count(ModelStatus.ERROR),
                "source": result.get("source", str(source)),
                "elapsed": result.get("elapsed", ""),
                "text": str(err),
            }
        )
        out_file.flush()


def run_jobs(
    *,
    prompt: Prompt,
    out_file: Path,
    file_mode: str,
    tasks: Sequence[Any],
    skipped: int,
    total: int,
    unit: str,
    verb: str,
    nothing_found: str,
    call: Callable[[Any, ThreadSessions], dict],
    threads: int,
    job_began: datetime,
    source_of: Callable[[Any], str] = str,
    text_of: Callable[[Any], str] | None = None,
) -> None:
    """
    Run call(task, sessions) over tasks, writing a row per task to out_file.

    Nothing to do because everything is already done is a normal, successful
    end of the job (return). Nothing to do because there was nothing usable to
    work on is an error (exit 1), which is what lets a shell chain such as
    `ocr_images.py ... && parse_text.py ...` work on a resumed run.

    unit/verb only shape the log lines, e.g. ("image(s)", "OCRed").
    source_of/text_of pull the log labels out of a task; tasks are image paths
    for the image jobs and OCR records for parse_text.
    """
    if not tasks:
        if skipped:
            logging.info(f"Nothing to do: {skipped} of {total} {unit} already done")
            log.job_elapsed(job_began)
            return
        logging.error(nothing_found)
        log.job_elapsed(job_began)
        raise SystemExit(1)

    statuses = StatusCounts()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with out_file.open(file_mode) as output_file:
        writer = csv.DictWriter(output_file, prompt.columns)
        if file_mode == "w":
            writer.writeheader()

        with (
            tqdm(total=len(tasks)) as pbar,
            ThreadPoolExecutor(max_workers=threads) as executor,
        ):
            sessions = ThreadSessions()

            futures = {executor.submit(call, task, sessions): task for task in tasks}

            try:
                for future in as_completed(futures):
                    task = futures[future]
                    source = source_of(task)
                    pbar.update(1)
                    result = future_result(
                        future,
                        source,
                        text_of(task) if text_of else "",
                        prompt,
                    )
                    write_row(writer, output_file, statuses, result, source)
            except KeyboardInterrupt:
                # Ctrl-C means stop now: drop the queued tasks instead of
                # waiting for the pool to drain every queued request.
                executor.shutdown(cancel_futures=True)
                raise
            finally:
                sessions.close_all()

    logging.info(
        f"{verb} {statuses.get(ModelStatus.SUCCESS)}/{len(tasks)} {unit}, "
        f"{statuses.get(ModelStatus.ERROR)} errored, {skipped} already done"
    )
    log.job_elapsed(job_began)
