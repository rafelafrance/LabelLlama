import logging
from typing import TYPE_CHECKING

import pandas as pd

from llama.prompts.prompt import REQUIRED_COLUMNS
from llama.results.model_status import ModelStatus
from llama.results.ocr_docs import read_results_csv

if TYPE_CHECKING:
    from pathlib import Path


class ParsedDocs:
    def __init__(
        self,
        parsed_file: Path,
        ocr_file: Path,
        prompt_columns: list[str],
        limit: int | None = None,
    ) -> None:
        if not prompt_columns:
            raise ValueError("There are no prompt columns")

        ocr_recs = self.read_ocr_records(ocr_file)

        self.parsed_records, self.file_mode = self.read_parsed_records(
            parsed_file, prompt_columns
        )
        already_done = {
            r.get("source")
            for r in self.parsed_records
            if r.get("source") and r.get("status", "").lower() == ModelStatus.SUCCESS
        }
        tasks = [
            rec for rec in ocr_recs if (rec.get("source") or "") not in already_done
        ]
        tasks = sorted(tasks, key=lambda rec: rec.get("source", ""))
        self.tasks = tasks[:limit]

    def read_ocr_records(self, ocr_file: Path) -> list[dict]:
        # Read he OCR CSV
        df = read_results_csv(ocr_file, "OCR results file")
        try:
            df = pd.read_csv(ocr_file, dtype=str).fillna("")
        except pd.errors.EmptyDataError:
            return []

        # CSV must have required columns
        missing = set(REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"OCR file is missing required columns: {missing_str}")

        df = self.successful_rows(df, "OCR")
        df = self.valid_source(df, "OCR")
        df = df[df["text"].str.strip() != ""]  # CSV records must have text

        return df.to_dict("records")

    def read_parsed_records(
        self,
        parsed_file: Path | None,
        prompt_columns: list[str],
    ) -> tuple[list[dict], str]:
        mode = "w"
        records = []

        if parsed_file and parsed_file.exists() and parsed_file.stat().st_size > 0:
            df = read_results_csv(parsed_file, "existing parsed file")
            if df is None:
                return records, mode

            # Make sure the current prompt and the results CSV overlapping columns
            expected_columns = set(REQUIRED_COLUMNS) | set(prompt_columns)
            if prompt_columns and expected_columns ^ set(df.columns):
                raise ValueError(
                    "Existing parsed file columns do not match the prompt columns"
                )

            df = self.successful_rows(df, "parsed")
            df = self.valid_source(df, "parsed")

            mode = "a"
            records = df.to_dict("records")
        return records, mode

    def successful_rows(self, df: pd.DataFrame, type_: str) -> pd.DataFrame:
        """Remove rows without a successful status."""
        keep = df["status"].str.lower() == ModelStatus.SUCCESS
        dropped = int((~keep).sum())
        if dropped:
            logging.warning(f"Skipping {dropped} {type_} row(s) that did not succeed")
        df = df[keep]
        return df

    def valid_source(self, df: pd.DataFrame, type_: str) -> pd.DataFrame:
        """Remove rows with an invalid source."""
        blank = df["source"].str.strip() == ""
        if blank.any():
            logging.warning(
                f"Ignoring {int(blank.sum())} {type_} row(s) with no source."
            )
        df = df[~blank]
        return df
