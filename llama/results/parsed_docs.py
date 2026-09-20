from pathlib import Path

from llama.prompts.prompt import REQUIRED_COLUMNS
from llama.results.base_docs import BaseDocs
from llama.results.model_status import ModelStatus


class ParsedDocs(BaseDocs):
    def __init__(
        self,
        parsed_file: Path,
        ocr_file: Path,
        prompt_columns: list[str],
        limit: int | None = None,
    ) -> None:
        if not prompt_columns:
            raise ValueError("There are no prompt columns")

        ocr_recs, _ = self.read_ocr_docs(ocr_file, successful_only=True)

        self.parsed_records, self.file_mode = self.read_parsed_records(
            parsed_file, prompt_columns
        )

        already_done = {
            str(Path(r["source"]).resolve())
            for r in self.parsed_records
            if ModelStatus.is_success(r.get("status"))
        }

        tasks = [
            rec for rec in ocr_recs if (rec.get("source") or "") not in already_done
        ]
        tasks = sorted(tasks, key=lambda rec: rec.get("source", ""))

        self.skipped = len(ocr_recs) - len(tasks)
        self.tasks = tasks[:limit]

    def read_parsed_records(
        self,
        parsed_file: Path | None,
        prompt_columns: list[str],
    ) -> tuple[list[dict], str]:
        mode = "w"
        records = []

        if parsed_file and parsed_file.exists() and parsed_file.stat().st_size > 0:
            df = self.read_results_csv(parsed_file, "existing parsed file")
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
            df = df.drop_duplicates(subset="source", keep="last")  # last wins

            mode = "a"
            records = df.to_dict("records")

        return records, mode
