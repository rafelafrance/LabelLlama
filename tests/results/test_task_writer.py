import csv
import io
import unittest
from concurrent.futures import Future
from types import SimpleNamespace
from unittest.mock import MagicMock

from llama.prompts.prompt import REQUIRED_COLUMNS
from llama.results.model_status import ModelStatus, StatusCounts
from llama.results.task_writer import MIN_TEXT_LEN, TaskWriter


def make_prompt(
    columns: list[str] | None = None, req_fields: list[str] | None = None
) -> SimpleNamespace:
    """
    Duck-type the prompt: expose only the two attributes
    TaskWriter.check() reads (columns and req_fields).
    """
    return SimpleNamespace(
        columns=columns if columns is not None else [],
        req_fields=req_fields or [],
    )


def make_task_writer(
    fieldnames: list[str], prompt: SimpleNamespace | None = None
) -> tuple[TaskWriter, io.StringIO]:
    out_file = io.StringIO()
    writer = csv.DictWriter(out_file, fieldnames)
    writer.writeheader()  # as the production callers do
    task_writer = TaskWriter(
        writer=writer,
        out_file=out_file,
        statuses=StatusCounts(),
        progress_bar=MagicMock(),
        prompt=prompt if prompt is not None else make_prompt(),
    )
    return task_writer, out_file


def read_rows(out_file: io.StringIO) -> list[dict]:
    out_file.seek(0)
    return list(csv.DictReader(out_file))


def done_future(result: dict) -> Future[dict]:
    future: Future[dict] = Future()
    future.set_result(result)
    return future


def failing_future(err: Exception | None = None) -> Future[dict]:
    future: Future[dict] = Future()
    future.set_exception(err if err is not None else RuntimeError("boom"))
    return future


def base_result(**overrides: object) -> dict:
    result = {
        "status": ModelStatus.SUCCESS,
        "source": "a.txt",
        "elapsed": "1.0",
        "text": "hello",
    }
    result.update(overrides)
    return result


class TestTaskWriter(unittest.TestCase):
    def test_write_success_row_01(self) -> None:
        tw, out = make_task_writer(REQUIRED_COLUMNS)
        tw.write(done_future(base_result()), source="a.txt")

        rows = read_rows(out)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "success")
        self.assertEqual(rows[0]["source"], "a.txt")
        self.assertEqual(rows[0]["elapsed"], "1.0")
        self.assertEqual(rows[0]["text"], "hello")
        self.assertEqual(tw.statuses.get(ModelStatus.SUCCESS), 1)
        tw.progress_bar.update.assert_called_once_with(1)

    def test_write_future_error_row_02(self) -> None:
        tw, out = make_task_writer(REQUIRED_COLUMNS)
        tw.write(failing_future(RuntimeError("boom")), source="a.txt")

        rows = read_rows(out)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "ERROR")
        self.assertEqual(rows[0]["source"], "a.txt")
        self.assertEqual(rows[0]["text"], "boom")
        self.assertEqual(tw.statuses.get(ModelStatus.ERROR), 1)

    def test_future_error_without_source_03(self) -> None:
        # A failing future with no source still produces one row
        tw, out = make_task_writer(REQUIRED_COLUMNS)
        tw.write(failing_future(RuntimeError("boom")))

        rows = read_rows(out)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "ERROR")
        self.assertEqual(tw.statuses.get(ModelStatus.ERROR), 1)

    def test_missing_required_field_is_error_04(self) -> None:
        # Parse writer: a required LLM field left empty is an error row
        columns = [*REQUIRED_COLUMNS, "scientificName"]
        prompt = make_prompt(columns=columns, req_fields=["scientificName"])
        tw, out = make_task_writer(columns, prompt=prompt)
        tw.write(
            done_future(base_result(scientificName="", text="")),
            source="a.txt",
            text="x" * MIN_TEXT_LEN,
        )

        rows = read_rows(out)
        self.assertEqual(rows[0]["status"], "ERROR")
        self.assertIn("Missing required field", rows[0]["text"])
        self.assertEqual(tw.statuses.get(ModelStatus.ERROR), 1)

    def test_hallucinated_column_is_error_05(self) -> None:
        # A result key the prompt does not define is an error row
        prompt = make_prompt(columns=REQUIRED_COLUMNS)
        tw, out = make_task_writer(REQUIRED_COLUMNS, prompt=prompt)
        tw.write(
            done_future(base_result(bogusKey="stray value")),
            source="a.txt",
        )

        rows = read_rows(out)
        self.assertEqual(rows[0]["status"], "ERROR")
        self.assertIn("bogusKey", rows[0]["text"])
        self.assertEqual(tw.statuses.get(ModelStatus.ERROR), 1)

    def test_empty_llm_output_long_text_is_error_06(self) -> None:
        # Parse writer with LLM columns and a long input text:
        # an empty extraction is an error, not a success row
        columns = [*REQUIRED_COLUMNS, "scientificName"]
        prompt = make_prompt(columns=columns)
        tw, out = make_task_writer(columns, prompt=prompt)
        tw.write(
            done_future(base_result(text="", scientificName="")),
            source="a.txt",
            text="x" * MIN_TEXT_LEN,
        )

        rows = read_rows(out)
        self.assertEqual(rows[0]["status"], "ERROR")
        self.assertIn("no output", rows[0]["text"].lower())
        self.assertEqual(tw.statuses.get(ModelStatus.ERROR), 1)

    def test_check_skipped_for_short_text_07(self) -> None:
        # A short input can legitimately yield nothing: keep it a success
        columns = [*REQUIRED_COLUMNS, "scientificName"]
        prompt = make_prompt(columns=columns)
        tw, out = make_task_writer(columns, prompt=prompt)
        tw.write(
            done_future(base_result(text="", scientificName="")),
            source="a.txt",
            text="x" * (MIN_TEXT_LEN - 1),
        )

        rows = read_rows(out)
        self.assertEqual(rows[0]["status"], "success")
        self.assertEqual(tw.statuses.get(ModelStatus.SUCCESS), 1)

    def test_check_applies_at_min_text_len_08(self) -> None:
        # Boundary: text of exactly MIN_TEXT_LEN is long enough
        columns = [*REQUIRED_COLUMNS, "scientificName"]
        prompt = make_prompt(columns=columns)
        tw, out = make_task_writer(columns, prompt=prompt)
        tw.write(
            done_future(base_result(text="", scientificName="")),
            source="a.txt",
            text="x" * MIN_TEXT_LEN,
        )

        rows = read_rows(out)
        self.assertEqual(rows[0]["status"], "ERROR")
        self.assertIn("no output", rows[0]["text"].lower())

    def test_ocr_style_success_row_09(self) -> None:
        # No LLM columns: the empty-output check is skipped entirely
        prompt = make_prompt(columns=REQUIRED_COLUMNS)
        tw, out = make_task_writer(REQUIRED_COLUMNS, prompt=prompt)
        tw.write(
            done_future(base_result(source="a.jpg", text="")),
            source="a.jpg",
        )

        rows = read_rows(out)
        self.assertEqual(rows[0]["status"], "success")
        self.assertEqual(tw.statuses.get(ModelStatus.SUCCESS), 1)

    def test_writer_value_error_fallback_row_10(self) -> None:
        # A result key the writer does not know triggers the fallback
        # error row, counted exactly once
        tw, out = make_task_writer(REQUIRED_COLUMNS)
        tw.write(
            done_future(base_result(hallucinatedKey="stray value")),
            source="a.txt",
        )

        self.assertEqual(tw.statuses.get(ModelStatus.SUCCESS), 0)
        self.assertEqual(tw.statuses.get(ModelStatus.ERROR), 1)
        rows = read_rows(out)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "ERROR")

    def test_missing_llm_key_written_as_empty_11(self) -> None:
        # A result lacking an LLM column key is written with an empty
        # value, not dropped
        columns = [*REQUIRED_COLUMNS, "scientificName"]
        prompt = make_prompt(columns=columns)
        tw, out = make_task_writer(columns, prompt=prompt)
        tw.write(
            done_future(base_result(text="")),
            source="a.txt",
            text="short input",
        )

        rows = read_rows(out)
        self.assertEqual(rows[0]["status"], "success")
        self.assertEqual(rows[0]["scientificName"], "")


if __name__ == "__main__":
    unittest.main()
