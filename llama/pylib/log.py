"""
Setup a logger and log basic information about a script.

Also time how long processes take.

This is not a high-performance timer, it is used to get a general idea of how long
certain processes take. I want the times in a format that I can easily report to
non-technical people.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Callable


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


_job_began: datetime | None = None


def job_began(
    file_name: str | Path | None = None, *, args: Namespace | None
) -> datetime:
    global _job_began

    started(file_name, args=args)
    _job_began = datetime.now()
    return _job_began


def job_elapsed(job_began: datetime) -> None:
    elapsed = datetime.now() - job_began
    msg = f"Job elapsed {elapsed}"
    logging.info(msg)
    finished()


def run_job(run: Callable[[Namespace], None], args: Namespace) -> None:
    """
    Run a script job function, exiting cleanly on expected errors.

    A bad prompt, an unreadable results file or columns that do not match the
    prompt all raise ValueError from the prompt and results modules. Those are
    user errors, not bugs, so report one line plus the job trailer instead of a
    stack trace, and exit non-zero. Anything else keeps its traceback.
    """
    try:
        run(args)
    except ValueError as err:
        logging.error(str(err))
        logging.debug("Job failed", exc_info=True)
        if _job_began is not None:
            job_elapsed(_job_began)
        raise SystemExit(1) from err


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
