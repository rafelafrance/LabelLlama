from dataclasses import dataclass, field, fields
from enum import StrEnum
from typing import TYPE_CHECKING

import pandas as pd

from llama.pylib import image_util

if TYPE_CHECKING:
    from pathlib import Path

MIN_SIZE = 1024


class OcrStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "ERROR"
    UNKNOWN = ""


@dataclass
class OcrModelArgs:
    api_host: str = "http://localhost:1234/v1"
    model_name: str = "chandra-ocr"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 120
    convert_html: bool = False
    threads: int = 2


@dataclass
class OcrResult:
    status: OcrStatus = OcrStatus.UNKNOWN
    source: str = ""
    elapsed: str = ""
    text: str = ""


@dataclass
class OcrDocs:
    image_dir: Path | None = None
    ocr_file: Path | None = None
    image_paths: list[Path] = field(default_factory=list)
    already_read: set[str] = field(default_factory=set)
    records: list[OcrResult] = field(default_factory=list)
    ocr_file_mode: str = "w"

    @classmethod
    def read_image_dir(
        cls, image_dir: Path, ocr_file: Path | None = None, limit: int | None = None
    ) -> OcrDocs:
        docs = cls(
            image_dir=image_dir,
            ocr_file=ocr_file,
        )
        docs.image_paths = image_util.get_images(image_dir, limit)

        if ocr_file and ocr_file.exists() and ocr_file.stat().st_size >= MIN_SIZE:
            docs.ocr_file_mode = "a"
            docs.records = [
                OcrResult(
                    status=r.get("status", ""),
                    source=r.get("source", ""),
                    elapsed=r.get("elapsed", ""),
                    text=r["text"],
                )
                for r in pd.read_csv(ocr_file, dtype=str).fillna("").to_dict("records")
            ]
            docs.already_read = {
                r.source
                for r in docs.records
                if r.source and r.status == OcrStatus.SUCCESS
            }
        return docs

    @property
    def column_names(self) -> list[str]:
        return [f.name for f in fields(OcrDocs)]

    @property
    def total(self) -> int:
        return len(self.image_paths)

    @property
    def previously_done(self) -> int:
        return len(self.already_read)

    @property
    def remaining(self) -> int:
        return self.total - self.previously_done

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.records if r.status == OcrStatus.ERROR)

    def to_do(self) -> list[Path]:
        return sorted(p for p in self.image_paths if str(p) not in self.already_read)
