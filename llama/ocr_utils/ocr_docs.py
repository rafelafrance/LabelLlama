from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

import pandas as pd

from llama.ocr_utils.ocr_result import OcrResult
from llama.ocr_utils.ocr_status import OcrStatus
from llama.pylib import image_util

if TYPE_CHECKING:
    from pathlib import Path

MIN_SIZE = 1024


@dataclass
class OcrDocs:
    image_dir: Path | None = None
    image_glob: str = ""
    image_paths: list[Path] = field(default_factory=list)
    ocr_file: Path | None = None
    ocr_file_mode: str = "w"
    ocr_records: list[OcrResult] = field(default_factory=list[OcrResult])
    ocr_success: set[str] = field(default_factory=set[str])
    tasks: list[Path] = field(default_factory=list)
    limit: int | None = None

    @classmethod
    def build(
        cls,
        image_dir: Path,
        image_glob: str = "",
        ocr_file: Path | None = None,
        limit: int | None = None,
    ) -> OcrDocs:
        docs = cls(
            image_dir=image_dir,
            image_glob=image_glob,
            ocr_file=ocr_file,
            limit=limit,
        )

        docs.image_paths = image_util.get_images(image_dir, image_glob)
        docs.image_paths = docs.image_paths[:limit]

        docs.ocr_records, docs.ocr_file_mode = docs._read_ocr_records(ocr_file)
        docs.ocr_success = docs._get_already_read()
        docs.tasks = docs._get_tasks()
        return docs

    def _read_ocr_records(self, ocr_file: Path | None) -> tuple[list[OcrResult], str]:
        mode = "w"
        records = []
        if ocr_file and ocr_file.exists() and ocr_file.stat().st_size >= MIN_SIZE:
            mode = "a"
            records = [
                OcrResult(
                    status=r.get("status", ""),
                    source=r.get("source", ""),
                    elapsed=r.get("elapsed", ""),
                    text=r["text"],
                )
                for r in pd.read_csv(ocr_file, dtype=str).fillna("").to_dict("records")
            ]
        return records, mode

    def _get_already_read(self) -> set[str]:
        return {
            r.source
            for r in self.ocr_records
            if r.source and r.status.lower() == OcrStatus.SUCCESS
        }

    def _get_tasks(self) -> list[Path]:
        return sorted(p for p in self.image_paths if str(p) not in self.ocr_success)

    @staticmethod
    def get_ocr_records(ocr_file: Path | None) -> list[OcrResult]:
        records = []
        if ocr_file:
            records = [
                OcrResult(
                    status=r.get("status", ""),
                    source=r.get("source", ""),
                    elapsed=r.get("elapsed", ""),
                    text=r["text"],
                )
                for r in pd.read_csv(ocr_file, dtype=str).fillna("").to_dict("records")
            ]
        return records

    @property
    def field_names(self) -> list[str]:
        return [f.name for f in fields(OcrResult)]
