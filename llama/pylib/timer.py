import logging
import time
from typing import TYPE_CHECKING

from llama.pylib import log

if TYPE_CHECKING:
    from argparse import Namespace
    from pathlib import Path


def job_began(
    file_name: str | Path | None = None, *, args: Namespace | None
) -> float:
    log.started(file_name, args=args)
    return time.perf_counter()


def job_elapsed(job_began: float) -> None:
    job_elapsed = time.perf_counter() - job_began
    msg = f"Job elapsed {job_elapsed:0.4f}"
    logging.info(msg)
    log.finished()


def elapsed(started: float, name: str = "") -> str:
    elapsed_ = str(time.perf_counter() - started)
    if name:
        msg = f"{name} elapsed {elapsed_:0.4f}"
        logging.info(msg)
    return elapsed_
