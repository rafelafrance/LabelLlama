from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pandas as pd

from llama.ocr_utils.ocr_docs import MIN_SIZE, OcrDocs
from llama.ocr_utils.ocr_result import OcrResult
from llama.parser_utils.parser_status import ParserStatus

if TYPE_CHECKING:
    from pathlib import Path

FIRST_COLUMNS = ["status", "source", "text", "elapsed"]


@dataclass
class ParsedDocs:
    ocr_file: Path | None = None
    ocr_records: list[OcrResult] = field(default_factory=list[OcrResult])
    parsed_file: Path | None = None
    parsed_file_mode: str = "w"
    parsed_records: list[dict] = field(default_factory=list[dict])
    already_parsed: set[str] = field(default_factory=set[str])
    tasks: list[OcrResult] = field(default_factory=list[OcrResult])
    limit: int | None = None

    @classmethod
    def build(
        cls, parsed_file: Path, ocr_file: Path, limit: int | None = None
    ) -> ParsedDocs:
        docs = cls(parsed_file=parsed_file, ocr_file=ocr_file, limit=limit)

        docs.ocr_records = OcrDocs.get_ocr_records(ocr_file)
        docs.ocr_records = docs.ocr_records[:limit]

        docs.parsed_records, docs.parsed_file_mode = docs._read_parsed_records(
            parsed_file
        )
        docs.already_parsed = docs._get_already_parsed()
        docs.tasks = docs._get_tasks()
        return docs

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
            if r["status"] == ParserStatus.SUCCESS
        }

    def _get_tasks(self) -> list[OcrResult]:
        return sorted(
            [r for r in self.ocr_records if r.source not in self.already_parsed],
            key=lambda r: r.source,
        )
