import logging
import sys
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
