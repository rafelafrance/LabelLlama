import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from llama.results.model_status import ModelStatus, StatusCounts
from llama.results.ocr_docs import COLUMNS

if TYPE_CHECKING:
    import csv
    import io
    from concurrent.futures import Future

    import tqdm

MIN_TEXT_LEN = 32


@dataclass
class TaskWriter:
    writer: csv.DictWriter
    out_file: io.StringIO
    statuses: StatusCounts
    progress_bar: tqdm.tqdm

    def write(
        self, future: Future[dict], source: Path | str = "", text: str = ""
    ) -> None:
        self.progress_bar.update(1)
        try:
            result = future.result()
            self.check(result, text)
        except Exception as err:
            name = Path(source).name if source else "unknown"
            logging.exception(f"Task error for: {name}")
            result = {
                "status": ModelStatus.ERROR,
                "source": str(source),
                "elapsed": "",
                "text": str(err),
            }

        try:
            result["status"] = self.statuses.count(result.get("status"))
            self.writer.writerow(result)
            self.out_file.flush()
        except ValueError as err:
            logging.exception(f"Parse error for: {Path(result['source']).name}")
            text = str(err)
            logging.exception(text)
            self.writer.writerow(
                {
                    "status": self.statuses.count(ModelStatus.ERROR),
                    "source": result.get("source", str(source)),
                    "elapsed": result.get("elapsed", ""),
                    "text": text,
                }
            )
            self.out_file.flush()

    def check(self, result: dict, text: str) -> None:
        """
        Raise ValueError if the model returned no usable output.

        This only applies to writers with LLM fields beyond the base COLUMNS
        (i.e., parse jobs, not OCR). When text is given and it is shorter
        than MIN_TEXT_LEN the check is skipped, since a small input can
        legitimately yield nothing. When no text is given (e.g., the input
        was an image) the check always applies.
        """
        llm_columns = [c for c in self.writer.fieldnames if c not in COLUMNS]
        if not llm_columns:
            return
        if text and len(text) < MIN_TEXT_LEN:
            return
        if all(not bool(result.get(c, "")) for c in llm_columns):
            raise ValueError("There is no output for this future.")
