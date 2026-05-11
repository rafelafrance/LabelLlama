"""
Time how long processes take.

This is not a high-performace timer, it is used to get a general idea of how long
certain processes take. I want the times in a format that I can easily report to
non-technical people. The times will live in CSV/TSV/whatever files and will get
looked at by others.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from llama.pylib import log

if TYPE_CHECKING:
    from argparse import Namespace
    from pathlib import Path


def job_began(
    file_name: str | Path | None = None, *, args: Namespace | None
) -> datetime:
    log.started(file_name, args=args)
    return datetime.now()


def job_elapsed(job_began: datetime) -> None:
    job_elapsed = datetime.now() - job_began
    msg = f"Job elapsed {job_elapsed}"
    logging.info(msg)
    log.finished()


def elapsed(started: datetime, name: str = "") -> str:
    elapsed_ = str(datetime.now() - started)
    if name:
        msg = f"{name} elapsed {elapsed_}"
        logging.info(msg)
    return elapsed_
