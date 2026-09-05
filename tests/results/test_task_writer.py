import csv
from concurrent.futures import Future
from io import StringIO
from typing import TYPE_CHECKING

from tqdm import tqdm

from llama.results.model_status import ModelStatus, StatusCounts
from llama.results.task_writer import MIN_TEXT_LEN, TaskWriter

if TYPE_CHECKING:
    import pytest


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


PARSE_COLUMNS = ["status", "source", "elapsed", "text", "scientificName", "family"]

LONG_TEXT = "label text long enough to pass the minimum length gate"


def make_parse_writer() -> tuple[csv.DictWriter, StringIO]:
    out_file = StringIO()
    writer = csv.DictWriter(out_file, PARSE_COLUMNS)
    writer.writeheader()
    return writer, out_file


def base_result(**fields: str) -> dict:
    result = {
        "status": "success",
        "source": "image.jpg",
        "elapsed": "0:00:01",
        "text": "",
    }
    result |= fields
    return result


def test_task_writer_marks_empty_object_result_as_error() -> None:
    """
    A model response of {} carries no LLM fields at all: that is "no
    output", not a success that would never be retried.
    """
    writer, out_file = make_parse_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_result(base_result())

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    task_writer.write(future, source="image.jpg", text=LONG_TEXT)

    assert statuses[ModelStatus.SUCCESS] == 0
    assert statuses[ModelStatus.ERROR] == 1
    assert "There is no output for this future." in out_file.getvalue()


def test_task_writer_marks_all_empty_fields_as_error() -> None:
    writer, out_file = make_parse_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_result(base_result(scientificName="", family=""))

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    task_writer.write(future, source="image.jpg", text=LONG_TEXT)

    assert statuses[ModelStatus.SUCCESS] == 0
    assert statuses[ModelStatus.ERROR] == 1
    assert "There is no output for this future." in out_file.getvalue()


def test_task_writer_writes_parse_success_when_a_field_has_a_value() -> None:
    writer, out_file = make_parse_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_result(base_result(scientificName="Quercus rubra", family=""))

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    task_writer.write(future, source="image.jpg", text=LONG_TEXT)

    assert statuses[ModelStatus.SUCCESS] == 1
    assert statuses[ModelStatus.ERROR] == 0
    assert "success,image.jpg" in out_file.getvalue()


def test_task_writer_marks_empty_object_as_error_without_input_text() -> None:
    """
    Flows with no input text (e.g. parse_images) must still be checked:
    the length gate only applies when text is actually provided.
    """
    writer, out_file = make_parse_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_result(base_result())

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    task_writer.write(future, source="image.jpg")

    assert statuses[ModelStatus.SUCCESS] == 0
    assert statuses[ModelStatus.ERROR] == 1


def test_task_writer_ocr_empty_result_is_success() -> None:
    """
    OCR writers have no LLM fields: an empty result is a legitimate success
    (e.g. a blank image), not "no output".
    """
    writer, out_file = make_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_result(
        {
            "status": "success",
            "source": "blank.jpg",
            "elapsed": "0:00:01",
            "text": "",
        }
    )

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    task_writer.write(future, source="blank.jpg")

    assert statuses[ModelStatus.SUCCESS] == 1
    assert statuses[ModelStatus.ERROR] == 0
    assert "success,blank.jpg" in out_file.getvalue()


def test_task_writer_short_text_all_empty_fields_is_success() -> None:
    """
    A short input can legitimately yield nothing (blank/illegible label), so
    the check is skipped and the row is a success: reruns will not re-parse
    it forever.
    """
    writer, out_file = make_parse_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_result(base_result(scientificName="", family=""))

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    task_writer.write(future, source="image.jpg", text="short label")

    assert statuses[ModelStatus.SUCCESS] == 1
    assert statuses[ModelStatus.ERROR] == 0
    assert "success,image.jpg" in out_file.getvalue()


def test_task_writer_check_skipped_below_min_text_length() -> None:
    writer, out_file = make_parse_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_result(base_result(scientificName="", family=""))

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    task_writer.write(future, source="image.jpg", text="x" * (MIN_TEXT_LEN - 1))

    assert statuses[ModelStatus.SUCCESS] == 1
    assert statuses[ModelStatus.ERROR] == 0


def test_task_writer_check_applies_at_min_text_length() -> None:
    writer, out_file = make_parse_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_result(base_result(scientificName="", family=""))

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    task_writer.write(future, source="image.jpg", text="x" * MIN_TEXT_LEN)

    assert statuses[ModelStatus.SUCCESS] == 0
    assert statuses[ModelStatus.ERROR] == 1


def test_task_writer_logs_unknown_when_source_missing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    writer, out_file = make_writer()
    progress_bar = tqdm()
    statuses = StatusCounts()
    future = Future()
    future.set_exception(RuntimeError("boom"))

    task_writer = TaskWriter(writer, out_file, statuses, progress_bar)
    with caplog.at_level("ERROR"):
        task_writer.write(future)

    assert "Task error for: unknown" in caplog.text
    assert statuses[ModelStatus.ERROR] == 1
