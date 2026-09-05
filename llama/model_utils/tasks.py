import logging
from pathlib import Path
from typing import TYPE_CHECKING

from llama.model_utils.model_status import ModelStatus, StatusCounts

if TYPE_CHECKING:
    import csv
    import io
    from concurrent.futures import Future

    from tqdm import tqdm



def complete_task(
    *,
    writer: csv.DictWriter,
    future: Future[dict],
    out_file: io.StringIO,
    statuses: StatusCounts,
    progress_bar: tqdm,
    source: Path | str = "",
) -> None:
    progress_bar.update(1)
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
        result["status"] = statuses.count(result.get("status"))
        writer.writerow(result)
        out_file.flush()
    except ValueError as err:
        logging.exception(f"Parse error for: {Path(result['source']).name}")
        text = str(err)
        logging.exception(text)
        writer.writerow(
            {
                "status": statuses.count(ModelStatus.ERROR),
                "source": result.get("source", str(source)),
                "elapsed": result.get("elapsed", ""),
                "text": text,
            }
        )
        out_file.flush()
