import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace


def setup_logger(file_name: str | Path | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if file_name:
        logging.getLogger().addHandler(logging.FileHandler(file_name))


def module_name() -> str:
    return Path(sys.argv[0]).stem


def started(
    file_name: str | Path | None = None, *, args: Namespace | None = None
) -> None:
    setup_logger(file_name)
    logging.info("=" * 80)
    msg = f"{module_name()} started"
    logging.info(msg)
    if args:
        log_args(args)


def finished() -> None:
    msg = f"{module_name()} finished"
    logging.info(msg)


def log_args(args: Namespace) -> None:
    for key, val in sorted(vars(args).items()):
        if key != "api_key":
            msg = f"Argument: {key} = {val}"
            logging.info(msg)


"""
Time how long processes take.

This is not a high-performance timer, it is used to get a general idea of how long
certain processes take. I want the times in a format that I can easily report to
non-technical people. The times will live in CSV/TSV/whatever files and will get
looked at by others.
"""


def job_began(
    file_name: str | Path | None = None, *, args: Namespace | None
) -> datetime:
    started(file_name, args=args)
    return datetime.now()


def job_elapsed(job_began: datetime) -> None:
    job_elapsed = datetime.now() - job_began
    msg = f"Job elapsed {job_elapsed}"
    logging.info(msg)
    finished()


def task_began(name: str = "") -> datetime:
    if name:
        logging.info(f"{name} started")
    return datetime.now()


def task_elapsed(started: datetime, name: str = "") -> str:
    elapsed_ = str(datetime.now() - started)
    if name:
        msg = f"{name} elapsed {elapsed_}"
        logging.info(msg)
    return elapsed_
