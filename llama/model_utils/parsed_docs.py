from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pandas as pd

from llama.model_utils.model_status import ModelStatus
from llama.model_utils.ocr_docs import MIN_SIZE, OcrDocs

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class ParsedDocs:
    ocr_file: Path | None = None
    ocr_records: list[dict] = field(default_factory=list[dict])
    parsed_file: Path | None = None
    file_mode: str = "w"
    parsed_records: list[dict] = field(default_factory=list[dict])
    already_done: set[str] = field(default_factory=set[str])
    tasks: list[dict] = field(default_factory=list[dict])
    limit: int | None = None

    @classmethod
    def build(
        cls, parsed_file: Path, ocr_file: Path, limit: int | None = None
    ) -> ParsedDocs:
        docs = cls(parsed_file=parsed_file, ocr_file=ocr_file, limit=limit)

        docs.ocr_records = OcrDocs.get_ocr_records(ocr_file)
        docs.ocr_records = docs.ocr_records[:limit]

        docs.parsed_records, docs.file_mode = docs._read_parsed_records(parsed_file)
        docs.already_done = docs._get_already_parsed()
        docs.tasks = docs._get_tasks()
        return docs

    @property
    def input_len(self) -> int:
        return len(self.ocr_records)

    def _read_parsed_records(self, parsed_file: Path | None) -> tuple[list[dict], str]:
        mode = "w"
        records = []
        if (
            parsed_file
            and parsed_file.exists()
            and parsed_file.stat().st_size >= MIN_SIZE
        ):
            mode = "a"
            records = pd.read_csv(parsed_file, dtype=str).fillna("").to_dict("records")
        return records, mode

    def _get_already_parsed(self) -> set[str]:
        return {
            r["source"]
            for r in self.parsed_records
            if r["status"] == ModelStatus.SUCCESS
        }

    def _get_tasks(self) -> list[dict]:
        return sorted(
            [r for r in self.ocr_records if r["source"] not in self.already_done],
            key=lambda r: r["source"],
        )
