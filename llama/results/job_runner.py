"""
The threaded work driver shared by ocr_images.py, parse_images.py and parse_text.py.

All three scripts do the same thing: run a model call over a list of tasks in a
thread pool and append one CSV row per task. Keeping the loop in one place means
the resume/exit policy, the CSV header, the HTTP sessions, the progress bar, the
error counting and the job trailer cannot drift apart between scripts.
"""

from __future__ import annotations

import csv
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING

from tqdm import tqdm

from llama.pylib import log
from llama.pylib.thread_sessions import ThreadSessions
from llama.results.model_status import ModelStatus, StatusCounts
from llama.results.task_writer import TaskWriter

# The image jobs share this: --image-dir is a single directory on purpose, so a
# tree of labels silently yields nothing.
NO_IMAGES_FOUND = (
    "No images found. --image-dir is not recursive; try --image-glob 'dir/**/*.jpg'"
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from datetime import datetime
    from pathlib import Path
    from typing import Any

    from llama.prompts.prompt import Prompt


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
            task_writer = TaskWriter(
                writer=writer,
                out_file=output_file,
                statuses=statuses,
                progress_bar=pbar,
                prompt=prompt,
            )

            futures = {executor.submit(call, task, sessions): task for task in tasks}

            try:
                for future in as_completed(futures):
                    task = futures[future]
                    task_writer.write(
                        future,
                        source=source_of(task),
                        text=text_of(task) if text_of else "",
                    )
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
