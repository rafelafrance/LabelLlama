from pathlib import Path
from typing import ClassVar

import pandas as pd

from llama.prompts.prompt import REQUIRED_COLUMNS
from llama.pylib import image_util
from llama.results.base_docs import BaseDocs
from llama.results.model_status import ModelStatus


class OcrDocs(BaseDocs):
    # -------------- ClassVars ---------------
    columns: ClassVar[list[str]] = REQUIRED_COLUMNS
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

        already_done = {
            str(Path(r["source"]).resolve())
            for r in self.ocr_records
            if ModelStatus.is_success(r.get("status"))
        }

        tasks = [p for p in image_paths if str(p.resolve()) not in already_done]

        self.image_count = len(image_paths)
        self.skipped = len(tasks)
        self.tasks = sorted(tasks, key=str)[:limit]

    def read_ocr_docs(
        self, ocr_file: Path | None, *, successful_only: bool = False
    ) -> tuple[list[dict], str]:
        mode = "w"
        records = []
        if ocr_file and ocr_file.exists() and ocr_file.stat().st_size > 0:
            df = self.read_results_csv(ocr_file, "OCR file")
            if df is None:
                return [], mode

            missing = set(REQUIRED_COLUMNS) - set(df.columns)
            if missing:
                missing_str = ", ".join(sorted(missing))
                raise ValueError(f"OCR file is missing required columns: {missing_str}")

            if successful_only:
                df = self.successful_rows(df, "OCR")

            df = self.valid_source(df, "OCR")
            df = df[df["text"].str.strip() != ""]  # CSV records must have text
            df = df.drop_duplicates(subset="source", keep="last")  # last wins

            mode = "a"
            records = df.to_dict("records")

        return records, mode
