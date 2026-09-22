import unittest

from llama.pylib import log


class TestRunJob(unittest.TestCase):
    def test_clean_run_returns_01(self) -> None:
        """A job that does not raise simply returns."""
        seen: list[str] = []

        def job(_args: object) -> None:
            seen.append("ran")

        log.run_job(job, "args")

        self.assertEqual(seen, ["ran"])

    def test_value_error_exits_one_02(self) -> None:
        """A ValueError from the job is logged and exits 1."""

        def job(_args: object) -> None:
            msg = "prompt.md is missing columns"
            raise ValueError(msg)

        with (
            self.assertRaises(SystemExit) as ctx,
            self.assertLogs(level="INFO") as logs,
        ):
            log.run_job(job, "args")

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("ERROR:root:prompt.md is missing columns", logs.output)

    def test_value_error_still_logs_the_job_trailer_03(self) -> None:
        """A failed job still logs elapsed time and finishing."""

        def job(_args: object) -> None:
            log.job_began(None, args=None)
            msg = "unreadable CSV"
            raise ValueError(msg)

        with self.assertRaises(SystemExit), self.assertLogs(level="INFO") as logs:
            log.run_job(job, "args")

        self.assertTrue(any("Job elapsed" in line for line in logs.output), logs.output)
        self.assertTrue(any("finished" in line for line in logs.output), logs.output)

    def test_unexpected_error_keeps_its_traceback_04(self) -> None:
        """An unexpected exception is raised, not turned into an exit."""

        def job(_args: object) -> None:
            msg = "a real bug"
            raise KeyError(msg)

        with self.assertRaises(KeyError):
            log.run_job(job, "args")

    def test_system_exit_from_job_passes_through_05(self) -> None:
        """A job that exits itself keeps its exit code."""

        def job(_args: object) -> None:
            raise SystemExit(1)

        with self.assertRaises(SystemExit) as ctx:
            log.run_job(job, "args")

        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
