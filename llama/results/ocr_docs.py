from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import pandas as pd

from llama.pylib import image_util
from llama.results.model_status import ModelStatus

if TYPE_CHECKING:
    from pathlib import Path


COLUMNS = ["status", "source", "elapsed", "text"]


def read_results_csv(path: Path, label: str) -> pd.DataFrame | None:
    """
    Read a results CSV into a DataFrame of strings.

    Returns None when the file holds no parseable content (the caller can
    then safely start the file over). Raises ValueError when the file exists
    but cannot be read as CSV, so a corrupt file is never silently
    overwritten.
    """
    try:
        return pd.read_csv(path, dtype=str).fillna("")
    except pd.errors.EmptyDataError:
        return None
    except (pd.errors.ParserError, UnicodeDecodeError) as err:
        raise ValueError(f"{label} is not a readable CSV file: {path} ({err})") from err


@dataclass
class OcrDocs:
    # -------------- ClassVars ---------------
    columns: ClassVar[list[str]] = COLUMNS
    # ----------------------------------------

    image_dir: Path | None = None
    image_glob: str = ""
    image_paths: list[Path] = field(default_factory=list)
    ocr_file: Path | None = None
    file_mode: str = "w"
    ocr_records: list[dict] = field(default_factory=list)
    already_done: set[str] = field(default_factory=set)
    tasks: list[Path | str] = field(default_factory=list)
    limit: int | None = None
    input_len: int = 0

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
        docs.input_len = len(docs.image_paths)
        docs.image_paths = docs.image_paths[:limit]

        docs.ocr_records, docs.file_mode = docs._read_ocr_records(ocr_file)
        docs.already_done = docs._get_already_read()
        docs.tasks = docs._get_tasks()
        return docs

    def _read_ocr_records(self, ocr_file: Path | None) -> tuple[list[dict], str]:
        mode = "w"
        records = []
        if ocr_file and ocr_file.exists() and ocr_file.stat().st_size > 0:
            df = read_results_csv(ocr_file, "OCR file")
            if df is not None:
                missing = set(COLUMNS) - set(df.columns)
                if missing:
                    missing_str = ", ".join(sorted(missing))
                    msg = f"OCR file is missing required columns: {missing_str}"
                    raise ValueError(msg)
                mode = "a"
                records = df.to_dict("records")
        return records, mode

    def _get_already_read(self) -> set[str]:
        return {
            r.get("source", "")
            for r in self.ocr_records
            if r.get("source") and ModelStatus.is_success(r.get("status"))
        }

    def _get_tasks(self) -> list[Path | str]:
        return sorted(p for p in self.image_paths if str(p) not in self.already_done)

    @staticmethod
    def get_ocr_records(ocr_file: Path | None) -> list[dict]:
        return (
            pd.read_csv(ocr_file, dtype=str).fillna("").to_dict("records")
            if ocr_file
            else []
        )
