import csv
import io
import time
import unittest
from concurrent.futures import Future
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from llama.prompts.prompt import REQUIRED_COLUMNS
from llama.results.job_runner import (
    MIN_TEXT_LEN,
    NO_IMAGES_FOUND,
    future_result,
    run_jobs,
    write_row,
)
from llama.results.model_status import ModelStatus, StatusCounts

COLUMNS = [*REQUIRED_COLUMNS, "scientificName"]


def make_prompt(
    columns: list[str] | None = None, req_fields: list[str] | None = None
) -> SimpleNamespace:
    """Duck-type the prompt: job_runner uses columns and req_fields."""
    return SimpleNamespace(
        columns=columns if columns is not None else REQUIRED_COLUMNS,
        req_fields=req_fields or [],
    )


def ok_call(task: Any, _sessions: Any) -> dict:
    return {
        "status": "success",
        "source": str(task),
        "elapsed": "0:01",
        "text": "Marsh",
    }


def fail_call(task: Any, _sessions: Any) -> dict:
    msg = f"nope: {task}"
    raise ValueError(msg)


def never_call(*_args: Any) -> dict:  # pragma: no cover - must not run
    msg = "call() must not run when there is nothing to do"
    raise AssertionError(msg)


def interrupt_call(*_args: Any) -> dict:
    raise KeyboardInterrupt


def read_rows(out_file: Path) -> list[dict]:
    with out_file.open(newline="") as handle:
        return list(csv.DictReader(handle))


def read_string_rows(out_file: io.StringIO) -> list[dict]:
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


def make_row_writer(
    fieldnames: list[str],
) -> tuple[csv.DictWriter, io.StringIO, StatusCounts]:
    out_file = io.StringIO()
    writer = csv.DictWriter(out_file, fieldnames)
    writer.writeheader()  # as the production caller does
    return writer, out_file, StatusCounts()


class TestRunJobs(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = TemporaryDirectory()
        self.tmp = Path(self._dir.name)
        patcher = patch("llama.results.job_runner.tqdm")
        self.addCleanup(patcher.stop)
        patcher.start()

    def tearDown(self) -> None:
        self._dir.cleanup()

    def run_driver(self, tasks: list, call: Any, **kwargs: Any) -> Path:
        out_file = self.tmp / "out.csv"
        skipped = kwargs.pop("skipped", 0)
        run_jobs(
            prompt=kwargs.pop("prompt", make_prompt()),
            out_file=out_file,
            file_mode=kwargs.pop("file_mode", "w"),
            tasks=tasks,
            skipped=skipped,
            total=kwargs.pop("total", len(tasks) + skipped),
            unit="image(s)",
            verb="OCRed",
            nothing_found=NO_IMAGES_FOUND,
            call=call,
            threads=kwargs.pop("threads", 2),
            job_began=datetime.now(),
            **kwargs,
        )
        return out_file

    def test_header_and_one_row_per_task_01(self) -> None:
        """Every task is written as its own row."""
        out_file = self.run_driver(["a.jpg", "b.jpg"], ok_call)

        rows = read_rows(out_file)
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["source"] for row in rows}, {"a.jpg", "b.jpg"})
        self.assertEqual({row["status"] for row in rows}, {"success"})

    def test_already_done_is_not_an_error_02(self) -> None:
        """A resume with nothing left to do exits 0 and writes no file."""
        out_file = self.run_driver([], never_call, skipped=5, total=5)

        self.assertFalse(out_file.exists())

    def test_nothing_found_exits_nonzero_03(self) -> None:
        """With no tasks at all the job exits 1 and writes no file."""
        with self.assertRaises(SystemExit) as ctx:
            self.run_driver([], never_call)

        self.assertEqual(ctx.exception.code, 1)
        self.assertFalse((self.tmp / "out.csv").exists())

    def test_call_exception_becomes_one_error_row_04(self) -> None:
        """An exception in call() becomes one ERROR row and the run continues."""
        with self.assertLogs(level="INFO") as logs:
            out_file = self.run_driver(["a.jpg"], fail_call)

        rows = read_rows(out_file)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "ERROR")
        self.assertIn("nope: a.jpg", rows[0]["text"])
        self.assertTrue(
            any("OCRed 0/1 image(s), 1 errored" in line for line in logs.output),
            logs.output,
        )

    def test_dict_tasks_use_source_of_and_text_of_05(self) -> None:
        """Dict tasks are labelled by source_of and text_of."""

        def record_call(ocr_rec: dict, _sessions: Any) -> dict:
            msg = ocr_rec["text"]
            raise RuntimeError(msg)

        tasks = [{"source": "a.jpg", "text": "Marsh with iris leaves"}]
        out_file = self.run_driver(
            tasks,
            record_call,
            prompt=make_prompt(COLUMNS),
            source_of=lambda rec: rec["source"],
            text_of=lambda rec: rec["text"],
        )

        rows = read_rows(out_file)
        self.assertEqual(rows[0]["source"], "a.jpg")
        self.assertIn("Marsh with iris leaves", rows[0]["text"])

    def test_append_mode_does_not_rewrite_header_06(self) -> None:
        """Append mode adds rows without repeating the header."""
        self.run_driver(["a.jpg"], ok_call)
        out_file = self.tmp / "out.csv"
        self.run_driver(["b.jpg"], ok_call, file_mode="a", skipped=1, total=2)

        lines = out_file.read_text().splitlines()
        self.assertEqual(lines.count(",".join(REQUIRED_COLUMNS)), 1)
        self.assertEqual(len(read_rows(out_file)), 2)

    def test_keyboard_interrupt_is_not_swallowed_07(self) -> None:
        """Ctrl-C in a worker is re-raised, not counted as an error row."""
        with self.assertRaises(KeyboardInterrupt):
            self.run_driver(["a.jpg", "b.jpg"], interrupt_call, threads=1)

    def test_keyboard_interrupt_cancels_queued_work_08(self) -> None:
        """Ctrl-C cancels the futures still queued behind it."""
        started: list[str] = []

        def slow_call(task: str, _sessions: Any) -> dict:
            started.append(task)
            if len(started) == 1:
                raise KeyboardInterrupt
            time.sleep(0.05)  # queued work that cancel_futures() should skip
            return ok_call(task, None)

        with self.assertRaises(KeyboardInterrupt):
            self.run_driver([f"{n}.jpg" for n in range(20)], slow_call, threads=1)

        self.assertLess(len(started), 20)


class TestFutureResult(unittest.TestCase):
    def test_success_result_passes_through_01(self) -> None:
        """A successful, valid future returns its result untouched."""
        result = future_result(done_future(base_result()), "a.txt", "", make_prompt())

        self.assertEqual(result, base_result())

    def test_future_error_becomes_error_row_02(self) -> None:
        """A failing future becomes an ERROR row carrying the exception text."""
        result = future_result(
            failing_future(RuntimeError("boom")), "a.txt", "", make_prompt()
        )

        self.assertEqual(result["status"], ModelStatus.ERROR)
        self.assertEqual(result["source"], "a.txt")
        self.assertEqual(result["text"], "boom")

    def test_future_error_without_source_03(self) -> None:
        """A failing future with no source still produces one row."""
        result = future_result(
            failing_future(RuntimeError("boom")), "", "", make_prompt()
        )

        self.assertEqual(result["status"], ModelStatus.ERROR)
        self.assertEqual(result["source"], "")

    def test_missing_required_field_is_error_04(self) -> None:
        """A required LLM field left empty is an error row."""
        prompt = make_prompt(columns=COLUMNS, req_fields=["scientificName"])
        result = future_result(
            done_future(base_result(scientificName="", text="")),
            "a.txt",
            "x" * MIN_TEXT_LEN,
            prompt,
        )

        self.assertEqual(result["status"], ModelStatus.ERROR)
        self.assertIn("Missing required field", result["text"])

    def test_empty_llm_output_long_text_is_error_05(self) -> None:
        """An empty extraction from a long text is an error, not a blank success."""
        prompt = make_prompt(columns=COLUMNS)
        result = future_result(
            done_future(base_result(text="", scientificName="")),
            "a.txt",
            "x" * MIN_TEXT_LEN,
            prompt,
        )

        self.assertEqual(result["status"], ModelStatus.ERROR)
        self.assertIn("no output", result["text"].lower())

    def test_check_skipped_for_short_text_06(self) -> None:
        """A short input can legitimately yield nothing: keep it a success."""
        prompt = make_prompt(columns=COLUMNS)
        result = future_result(
            done_future(base_result(text="", scientificName="")),
            "a.txt",
            "x" * (MIN_TEXT_LEN - 1),
            prompt,
        )

        self.assertEqual(result["status"], ModelStatus.SUCCESS)

    def test_check_applies_at_min_text_len_07(self) -> None:
        """Boundary: text of exactly MIN_TEXT_LEN is long enough."""
        prompt = make_prompt(columns=COLUMNS)
        result = future_result(
            done_future(base_result(text="", scientificName="")),
            "a.txt",
            "x" * MIN_TEXT_LEN,
            prompt,
        )

        self.assertEqual(result["status"], ModelStatus.ERROR)
        self.assertIn("no output", result["text"].lower())

    def test_ocr_style_result_passes_08(self) -> None:
        """No LLM columns: the empty-output check is skipped entirely."""
        prompt = make_prompt()
        result = future_result(
            done_future(base_result(source="a.jpg", text="")), "a.jpg", "", prompt
        )

        self.assertEqual(result["status"], ModelStatus.SUCCESS)


class TestWriteRow(unittest.TestCase):
    def test_success_row_written_and_counted_01(self) -> None:
        """A valid result becomes one row and its status is counted."""
        writer, out, statuses = make_row_writer(REQUIRED_COLUMNS)
        write_row(writer, out, statuses, base_result())

        rows = read_string_rows(out)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "success")
        self.assertEqual(rows[0]["source"], "a.txt")
        self.assertEqual(rows[0]["elapsed"], "1.0")
        self.assertEqual(rows[0]["text"], "hello")
        self.assertEqual(statuses.get(ModelStatus.SUCCESS), 1)

    def test_hallucinated_column_is_fallback_row_02(self) -> None:
        """A result key the writer does not know falls back to one ERROR row."""
        writer, out, statuses = make_row_writer(REQUIRED_COLUMNS)
        write_row(writer, out, statuses, base_result(bogusKey="stray value"), "a.txt")

        self.assertEqual(statuses.get(ModelStatus.SUCCESS), 0)
        self.assertEqual(statuses.get(ModelStatus.ERROR), 1)
        rows = read_string_rows(out)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "ERROR")
        self.assertIn("bogusKey", rows[0]["text"])

    def test_missing_llm_key_written_as_empty_03(self) -> None:
        """A result missing an LLM column key is written as an empty value."""
        writer, out, statuses = make_row_writer(COLUMNS)
        write_row(writer, out, statuses, base_result(text=""), "a.txt")

        rows = read_string_rows(out)
        self.assertEqual(rows[0]["status"], "success")
        self.assertEqual(rows[0]["scientificName"], "")


if __name__ == "__main__":
    unittest.main()
