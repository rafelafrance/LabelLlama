import csv
import time
import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from llama.prompts.prompt import REQUIRED_COLUMNS
from llama.results.job_runner import NO_IMAGES_FOUND, run_jobs

COLUMNS = [*REQUIRED_COLUMNS, "scientificName"]


def make_prompt(columns: list[str] | None = None) -> SimpleNamespace:
    """Duck-type the prompt: run_jobs and TaskWriter use columns and req_fields."""
    return SimpleNamespace(
        columns=columns if columns is not None else REQUIRED_COLUMNS,
        req_fields=[],
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
        out_file = self.run_driver(["a.jpg", "b.jpg"], ok_call)

        rows = read_rows(out_file)
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["source"] for row in rows}, {"a.jpg", "b.jpg"})
        self.assertEqual({row["status"] for row in rows}, {"success"})

    def test_already_done_is_not_an_error_02(self) -> None:
        out_file = self.run_driver([], never_call, skipped=5, total=5)

        self.assertFalse(out_file.exists())

    def test_nothing_found_exits_nonzero_03(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            self.run_driver([], never_call)

        self.assertEqual(ctx.exception.code, 1)
        self.assertFalse((self.tmp / "out.csv").exists())

    def test_call_exception_becomes_one_error_row_04(self) -> None:
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
        self.run_driver(["a.jpg"], ok_call)
        out_file = self.tmp / "out.csv"
        self.run_driver(["b.jpg"], ok_call, file_mode="a", skipped=1, total=2)

        lines = out_file.read_text().splitlines()
        self.assertEqual(lines.count(",".join(REQUIRED_COLUMNS)), 1)
        self.assertEqual(len(read_rows(out_file)), 2)

    def test_keyboard_interrupt_is_not_swallowed_07(self) -> None:
        with self.assertRaises(KeyboardInterrupt):
            self.run_driver(["a.jpg", "b.jpg"], interrupt_call, threads=1)

    def test_keyboard_interrupt_cancels_queued_work_08(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
