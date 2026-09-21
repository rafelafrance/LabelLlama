from pathlib import Path
from typing import ClassVar

from llama.prompts.prompt import REQUIRED_COLUMNS
from llama.pylib import image_util
from llama.results import doc_utils
from llama.results.model_status import ModelStatus


class OcrDocs:
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

        self.ocr_docs, self.file_mode = self.read_ocr_docs(ocr_file)

        already_done = {
            str(Path(doc["source"]).resolve())
            for doc in self.ocr_docs
            if ModelStatus.is_success(doc.get("status"))
        }

        tasks = [p for p in image_paths if str(p.resolve()) not in already_done]

        self.image_count = len(image_paths)
        self.skipped = len(tasks)
        self.tasks = sorted(tasks, key=str)[:limit]

    @staticmethod
    def read_ocr_docs(
        ocr_file: Path | None, *, successful_only: bool = False
    ) -> tuple[list[dict], str]:
        mode = "w"
        records = []
        if ocr_file and ocr_file.exists() and ocr_file.stat().st_size > 0:
            df = doc_utils.read_results_csv(ocr_file, "OCR file")
            if df is None:
                return [], mode

            missing = set(REQUIRED_COLUMNS) - set(df.columns)
            if missing:
                missing_str = ", ".join(sorted(missing))
                raise ValueError(f"OCR file is missing required columns: {missing_str}")

            if successful_only:
                df = doc_utils.successful_rows(df, "OCR")

            df = doc_utils.valid_source(df, "OCR")
            df = df[df["text"].str.strip() != ""]  # CSV records must have text
            df = df.drop_duplicates(subset="source", keep="last")  # last wins

            mode = "a"
            records = df.to_dict("records")

        return records, mode
