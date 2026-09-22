import logging
from typing import TYPE_CHECKING

import pandas as pd

from llama.results.model_status import ModelStatus

if TYPE_CHECKING:
    from pathlib import Path


def read_results_csv(path: Path, label: str) -> pd.DataFrame | None:
    """
    Read a results CSV into a DataFrame of strings.

    Returns None when the file holds no parseable content (the caller can
    then safely start the file over). Raises an error when the file exists
    but cannot be read as CSV, so a corrupt file is never silently
    overwritten.
    """
    try:
        return pd.read_csv(path, dtype=str).fillna("")
    except pd.errors.EmptyDataError:
        return None
    except (pd.errors.ParserError, UnicodeDecodeError) as err:
        raise ValueError(f"{label} is not a readable CSV file: {path} ({err})") from err


def successful_rows(df: pd.DataFrame, type_: str) -> pd.DataFrame:
    """Remove rows without a successful status."""
    keep = df["status"].map(ModelStatus.is_success).astype(bool)
    dropped = int((~keep).sum())
    if dropped:
        logging.warning(f"Skipping {dropped} {type_} row(s) that did not succeed")
    df = df[keep]
    return df


def valid_source(df: pd.DataFrame, type_: str) -> pd.DataFrame:
    """Remove rows with an invalid source."""
    blank = df["source"].str.strip() == ""
    if blank.any():
        logging.warning(f"Ignoring {int(blank.sum())} {type_} row(s) with no source.")
    df = df[~blank]
    return df
