from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pandas as pd

from llama.model_utils.model_status import ModelStatus
from llama.model_utils.ocr_docs import MIN_SIZE

if TYPE_CHECKING:
    from pathlib import Path


REQUIRED_OCR_COLUMNS = {"source", "text"}


@dataclass
class ParsedDocs:
    ocr_file: Path | None = None
    ocr_records: list[dict] = field(default_factory=list)
    parsed_file: Path | None = None
    file_mode: str = "w"
    parsed_records: list[dict] = field(default_factory=list)
    already_done: set[str] = field(default_factory=set)
    tasks: list[dict] = field(default_factory=list)
    limit: int | None = None

    @classmethod
    def build(
        cls,
        parsed_file: Path,
        ocr_file: Path,
        limit: int | None = None,
        expected_columns: list[str] | None = None,
    ) -> ParsedDocs:
        docs = cls(parsed_file=parsed_file, ocr_file=ocr_file, limit=limit)

        docs.ocr_records = docs._read_ocr_records(ocr_file)
        docs.ocr_records = docs.ocr_records[:limit]

        docs.parsed_records, docs.file_mode = docs._read_parsed_records(
            parsed_file, expected_columns
        )
        docs.already_done = docs._get_already_parsed()
        docs.tasks = docs._get_tasks()
        return docs

    @property
    def input_len(self) -> int:
        return len(self.ocr_records)

    def _read_ocr_records(self, ocr_file: Path) -> list[dict]:
        df = pd.read_csv(ocr_file, dtype=str).fillna("")
        missing = REQUIRED_OCR_COLUMNS - set(df.columns)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"OCR file is missing required columns: {missing_str}")
        return df.to_dict("records")

    def _read_parsed_records(
        self,
        parsed_file: Path | None,
        expected_columns: list[str] | None = None,
    ) -> tuple[list[dict], str]:
        mode = "w"
        records = []
        if (
            parsed_file
            and parsed_file.exists()
            and parsed_file.stat().st_size >= MIN_SIZE
        ):
            mode = "a"
            df = pd.read_csv(parsed_file, dtype=str).fillna("")
            if expected_columns and list(df.columns) != expected_columns:
                raise ValueError(
                    "Existing parsed file columns do not match the prompt columns"
                )
            records = df.to_dict("records")
        return records, mode

    def _get_already_parsed(self) -> set[str]:
        return {
            r["source"]
            for r in self.parsed_records
            if ModelStatus.is_success(r.get("status"))
        }

    def _get_tasks(self) -> list[dict]:
        return sorted(
            [r for r in self.ocr_records if r["source"] not in self.already_done],
            key=lambda r: r["source"],
        )
