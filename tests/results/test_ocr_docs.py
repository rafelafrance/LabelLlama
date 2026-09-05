"""
Resume behavior for OcrDocs.

An existing OCR file must be appended, never truncated, unless it is
empty or unreadable.
"""

import csv
from typing import TYPE_CHECKING

import pytest

from llama.results.ocr_docs import COLUMNS, OcrDocs

if TYPE_CHECKING:
    from pathlib import Path

SUCCESS_ROW = {
    "status": "success",
    "source": "a.jpg",
    "elapsed": "0:00:01",
    "text": "label a",
}


def write_ocr_file(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def test_small_ocr_file_is_appended_not_truncated(tmp_path: Path) -> None:
    ocr = tmp_path / "ocr.csv"
    write_ocr_file(ocr, [SUCCESS_ROW])
    assert ocr.stat().st_size < 1024

    docs = OcrDocs.build(tmp_path, "", ocr, None)

    assert docs.file_mode == "a"
    assert docs.already_done == {"a.jpg"}
    assert docs.tasks == []


def test_ocr_file_missing_columns_raises(tmp_path: Path) -> None:
    ocr = tmp_path / "ocr.csv"
    with ocr.open("w", newline="") as f:
        writer = csv.DictWriter(f, ["source", "text"])
        writer.writeheader()
        writer.writerow({"source": "a.jpg", "text": "x"})

    with pytest.raises(ValueError, match="missing required columns"):
        OcrDocs.build(tmp_path, "", ocr, None)
