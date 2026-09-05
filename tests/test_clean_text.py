"""
Tests for llama.clean_text failure handling.

Rows that fail cleaning must not disappear silently: the good rows are still
written out, the failures are reported, and the job exits non-zero.
"""

import argparse
import csv
from pathlib import Path

import pytest

from llama.clean_text import postprocess_fields
from llama.prompts.base_prompt import Thinking
from llama.prompts.parser_prompt import ParserPrompt

PROMPT = Path("prompts/herbarium_v2.md")


class FakeField:
    """A stand-in LLM field: fails to clean any text containing 'BOOM'."""

    def __init__(self, text: str = "", value: str = "") -> None:
        if "BOOM" in text:
            raise ValueError("simulated clean failure")
        self.value = value

    @classmethod
    def get_field_names(cls) -> list[str]:
        return ["value"]

    @classmethod
    def get_visible_fields(cls) -> list[str]:
        return ["value"]


class FakeCleaner:
    def __init__(self) -> None:
        self.llm_field_classes = {"fakeField": FakeField}
        self.calc_field_classes = {}

    @classmethod
    def load(cls, _prompt_path: object) -> FakeCleaner:
        return cls()


def write_parsed_file(tmp_path: Path, *, fail_second: bool) -> None:
    prompt = ParserPrompt(
        prompt=PROMPT,
        model_id="",
        temperature=None,
        max_tokens=None,
        thinking=Thinking.USE_SERVER,
    )
    columns = list(prompt.columns)
    rows = [
        {
            "status": "success",
            "source": "a.jpg",
            "elapsed": "0:00:01",
            "text": "fine label",
        },
        {
            "status": "success",
            "source": "b.jpg",
            "elapsed": "0:00:01",
            "text": "BOOM label" if fail_second else "fine label two",
        },
    ]
    with (tmp_path / "parsed.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


def make_args(tmp_path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        parsed_file=tmp_path / "parsed.csv",
        clean_file=tmp_path / "out" / "clean.csv",
        prompt=PROMPT,
        log_file=None,
        notes=None,
        limit=None,
    )


def test_clean_text_keeps_good_rows_and_fails_job(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr("llama.clean_text.ParserCleaner", FakeCleaner)
    write_parsed_file(tmp_path, fail_second=True)
    args = make_args(tmp_path)

    with caplog.at_level("ERROR"), pytest.raises(SystemExit) as excinfo:
        postprocess_fields(args)

    assert excinfo.value.code == 1
    assert "b.jpg" in caplog.text

    with args.clean_file.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert [r["source"] for r in rows] == ["a.jpg"]


def test_clean_text_success_writes_all_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("llama.clean_text.ParserCleaner", FakeCleaner)
    write_parsed_file(tmp_path, fail_second=False)
    args = make_args(tmp_path)

    postprocess_fields(args)  # no SystemExit

    with args.clean_file.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert [r["source"] for r in rows] == ["a.jpg", "b.jpg"]
