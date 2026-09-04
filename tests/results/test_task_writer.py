import csv
from concurrent.futures import Future
from io import StringIO

from tqdm import tqdm

from llama.results.model_status import ModelStatus, StatusCounts
from llama.results.task_writer import TaskWriter


def make_writer() -> tuple[csv.DictWriter, StringIO]:
    out_file = StringIO()
    writer = csv.DictWriter(out_file, ["status", "source", "elapsed", "text"])
    writer.writeheader()
    return writer, out_file


def test_task_writer_writes_successful_future() -> None:
    writer, out_file = make_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_result(
        {
            "status": "SUCCESS",
            "source": "image.jpg",
            "elapsed": "0:00:01",
            "text": "label text",
        }
    )

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    task_writer.write(future, source="image.jpg")

    assert progress_bar.n == 1
    assert statuses[ModelStatus.SUCCESS] == 1
    assert "success,image.jpg,0:00:01,label text" in out_file.getvalue()


def test_task_writer_converts_future_exception_to_error_row() -> None:
    writer, out_file = make_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_exception(RuntimeError("boom"))

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    task_writer.write(future, source="image.jpg")

    assert progress_bar.n == 1
    assert statuses[ModelStatus.ERROR] == 1
    assert "ERROR,image.jpg,,boom" in out_file.getvalue()


def test_task_writer_writes_fallback_error_row_for_extra_fields() -> None:
    writer, out_file = make_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_result(
        {
            "status": "success",
            "source": "image.jpg",
            "elapsed": "0:00:01",
            "text": "label text",
            "extra": "not in csv header",
        }
    )

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    task_writer.write(future, source="image.jpg")

    assert progress_bar.n == 1
    assert statuses[ModelStatus.SUCCESS] == 1
    assert statuses[ModelStatus.ERROR] == 1
    assert "ERROR,image.jpg,0:00:01," in out_file.getvalue()
