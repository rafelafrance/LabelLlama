from pathlib import Path

from llama.prompts.prompt import REQUIRED_COLUMNS
from llama.results import doc_utils
from llama.results.ocr_docs import OcrDocs


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

        ocr_docs, _ = OcrDocs.read_ocr_docs(ocr_file, successful_only=True)

        self.parsed_docs, self.file_mode = self.read_parsed_docs(
            parsed_file, prompt_columns
        )

        already_done = {str(Path(r["source"]).resolve()) for r in self.parsed_docs}

        tasks = [
            doc
            for doc in ocr_docs
            if str(Path(doc.get("source", "")).resolve()) not in already_done
        ]

        self.ocr_count = len(ocr_docs)
        self.skipped = self.ocr_count - len(tasks)
        self.tasks = tasks[:limit]

    @staticmethod
    def read_parsed_docs(
        parsed_file: Path | None,
        prompt_columns: list[str],
        *,
        strict_columns: bool = True,
    ) -> tuple[list[dict], str]:
        mode = "w"
        records = []

        if parsed_file and parsed_file.exists() and parsed_file.stat().st_size > 0:
            df = doc_utils.read_results_csv(parsed_file, "existing parsed file")
            if df is None:
                return records, mode

            # Make sure the current prompt and the results CSV overlapping columns
            expected_columns = set(REQUIRED_COLUMNS) | set(prompt_columns)
            extra = ", ".join(sorted(set(df.columns) - expected_columns))
            missing = ", ".join(sorted(expected_columns - set(df.columns)))
            if strict_columns and (extra or missing):
                raise ValueError(
                    f"{parsed_file} columns do not match the prompt: "
                    f"extra=[{extra}] missing=[{missing}]"
                )
            if not strict_columns and missing:
                raise ValueError(f"{parsed_file} is missing prompt columns: {missing}")

            df = doc_utils.successful_rows(df, "parsed")
            df = doc_utils.valid_source(df, "parsed")
            df = df.drop_duplicates(subset="source", keep="last")  # last wins

            mode = "a"
            records = df.to_dict("records")

        return records, mode
