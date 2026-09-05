"""
Resume behavior for ParsedDocs.

An existing parsed file must be appended, never truncated, unless it is
empty or unreadable. The old 1024-byte MIN_SIZE gate truncated valid files
with real results whenever they happened to be smaller than 1024 bytes.
"""

import csv
from typing import TYPE_CHECKING

import pytest

from llama.prompts.ocr_prompt import FIRST_COLUMNS
from llama.results.parsed_docs import ParsedDocs

if TYPE_CHECKING:
    from pathlib import Path

COLUMNS = [*FIRST_COLUMNS, "scientificName", "family"]

SUCCESS_ROW = {
    "status": "success",
    "source": "a.jpg",
    "elapsed": "0:00:01",
    "text": "label a",
    "scientificName": "Quercus rubra",
    "family": "Fagaceae",
}


def write_ocr_file(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, ["source", "text"])
        writer.writeheader()
        writer.writerows(rows)


def write_parsed_file(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def ocr_file(tmp_path: Path) -> Path:
    path = tmp_path / "ocr.csv"
    write_ocr_file(
        path,
        [
            {"source": "a.jpg", "text": "label a"},
            {"source": "b.jpg", "text": "label b"},
        ],
    )
    return path


def test_small_parsed_file_is_appended_not_truncated(
    ocr_file: Path, tmp_path: Path
) -> None:
    parsed = tmp_path / "parsed.csv"
    write_parsed_file(parsed, [SUCCESS_ROW])
    # This is the case the old MIN_SIZE gate got wrong: a valid file with
    # real results but fewer than 1024 bytes.
    assert parsed.stat().st_size < 1024

    docs = ParsedDocs.build(parsed, ocr_file, None, expected_columns=COLUMNS)

    assert docs.file_mode == "a"
    assert docs.already_done == {"a.jpg"}
    assert [task["source"] for task in docs.tasks] == ["b.jpg"]


def test_header_only_parsed_file_is_appended(ocr_file: Path, tmp_path: Path) -> None:
    parsed = tmp_path / "parsed.csv"
    write_parsed_file(parsed, [])

    docs = ParsedDocs.build(parsed, ocr_file, None, expected_columns=COLUMNS)

    assert docs.file_mode == "a"
    assert docs.already_done == set()
    assert [task["source"] for task in docs.tasks] == ["a.jpg", "b.jpg"]


def test_empty_parsed_file_is_rewritten(ocr_file: Path, tmp_path: Path) -> None:
    parsed = tmp_path / "parsed.csv"
    parsed.write_bytes(b"")

    docs = ParsedDocs.build(parsed, ocr_file, None, expected_columns=COLUMNS)

    assert docs.file_mode == "w"
    assert len(docs.tasks) == 2


def test_missing_parsed_file_is_written(ocr_file: Path, tmp_path: Path) -> None:
    parsed = tmp_path / "does_not_exist.csv"

    docs = ParsedDocs.build(parsed, ocr_file, None, expected_columns=COLUMNS)

    assert docs.file_mode == "w"
    assert len(docs.tasks) == 2


def test_parsed_file_with_wrong_columns_raises(ocr_file: Path, tmp_path: Path) -> None:
    parsed = tmp_path / "parsed.csv"
    write_parsed_file(parsed, [SUCCESS_ROW])

    with pytest.raises(ValueError, match="columns do not match"):
        ParsedDocs.build(parsed, ocr_file, None, expected_columns=[*COLUMNS, "extra"])


def test_unreadable_parsed_file_raises(ocr_file: Path, tmp_path: Path) -> None:
    parsed = tmp_path / "parsed.csv"
    parsed.write_text('status,source\n"unterminated,\n')

    with pytest.raises(ValueError, match="not a readable CSV"):
        ParsedDocs.build(parsed, ocr_file, None, expected_columns=COLUMNS)
