from pathlib import Path
from typing import ClassVar

import pandas as pd

from llama.prompts.prompt import FIRST_COLUMNS
from llama.pylib import image_util
from llama.results.model_status import ModelStatus


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


class OcrDocs:
    # -------------- ClassVars ---------------
    columns: ClassVar[list[str]] = FIRST_COLUMNS
    # ----------------------------------------

    def __init__(
        self,
        image_dir: Path,
        image_glob: str = "",
        ocr_file: Path | None = None,
        limit: int | None = None,
    ) -> None:
        image_paths = image_util.get_images(image_dir, image_glob)

        self.ocr_records, self.file_mode = self.read_ocr_records(ocr_file)

        self.already_done = {
            str(Path(r["source"]).resolve())
            for r in self.ocr_records
            if r.get("source") and r.get("status", "").lower() == ModelStatus.SUCCESS
        }

        pending = [p for p in image_paths if str(p.resolve()) not in self.already_done]
        self.image_count = len(image_paths)
        self.skipped = len(image_paths) - len(pending)
        self.tasks = sorted(pending, key=str)[:limit]

    def read_ocr_records(self, ocr_file: Path | None) -> tuple[list[dict], str]:
        mode = "w"
        records = []
        if ocr_file and ocr_file.exists():
            df = read_results_csv(ocr_file, "OCR file")
            if df is None:
                return [], mode
            missing = set(FIRST_COLUMNS) - set(df.columns)
            if missing:
                missing_str = ", ".join(sorted(missing))
                msg = f"OCR file is missing required columns: {missing_str}"
                raise ValueError(msg)
            mode = "a"
            records = df.to_dict("records")
        return records, mode
