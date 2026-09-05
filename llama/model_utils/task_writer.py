import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from llama.model_utils.model_status import ModelStatus, StatusCounts

if TYPE_CHECKING:
    import csv
    import io
    from concurrent.futures import Future

    import tqdm


@dataclass
class TaskWriter:
    writer: csv.DictWriter
    out_file: io.StringIO
    statuses: StatusCounts
    progress_bar: tqdm.tqdm

    def write(self, future: Future[dict], source: Path | str = "") -> None:
        self.progress_bar.update(1)
        try:
            result = future.result()
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
