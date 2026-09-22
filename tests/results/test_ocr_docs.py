import csv
import tempfile
import unittest
from pathlib import Path

from llama.results.doc_utils import read_results_csv
from llama.results.ocr_docs import OcrDocs

COLUMNS = ["status", "source", "elapsed", "text"]


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


class TestOcrDocs(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.a = self.tmp / "a.png"
        self.b = self.tmp / "b.jpg"
        self.a.write_bytes(b"png")
        self.b.write_bytes(b"jpg")
        (self.tmp / "notes.txt").write_text("not an image")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_read_results_csv_basic_01(self) -> None:
        """A readable results CSV is returned as a DataFrame."""
        path = self.tmp / "res.csv"
        write_csv(
            path,
            COLUMNS,
            [["success", "a.png", "1.0", "hello"], ["ERROR", "b.png", "", ""]],
        )

        df = read_results_csv(path, "OCR file")

        self.assertIsNotNone(df)
        # Missing cells become "", everything stays a string
        self.assertEqual(df.iloc[1]["elapsed"], "")
        self.assertEqual(df.iloc[0]["text"], "hello")
        self.assertIsInstance(df.iloc[0]["elapsed"], str)

    def test_read_results_csv_empty_file_returns_none_02(self) -> None:
        """An empty file returns None so callers start fresh."""
        path = self.tmp / "empty.csv"
        path.write_bytes(b"")

        self.assertIsNone(read_results_csv(path, "OCR file"))

    def test_read_results_csv_corrupt_raises_value_error_03(self) -> None:
        """A corrupt CSV raises ValueError naming the file."""
        path = self.tmp / "bad.csv"
        # Unbalanced quote -> pandas ParserError
        path.write_text('status,source\n"unterminated,2\n', encoding="utf-8")

        with self.assertRaises(ValueError) as ctx:
            read_results_csv(path, "OCR file")

        # The label and the path help the user find the bad file
        self.assertIn("OCR file", str(ctx.exception))
        self.assertIn(str(path), str(ctx.exception))

    def test_read_results_csv_bad_encoding_raises_04(self) -> None:
        """Undecodable bytes raise ValueError naming the file."""
        path = self.tmp / "bin.csv"
        path.write_bytes(b"\xff\xfe\x00\x81\n\x00")

        with self.assertRaises(ValueError):
            read_results_csv(path, "OCR file")

    def test_init_without_ocr_file_05(self) -> None:
        """With no OCR file every image becomes a task."""
        docs = OcrDocs(self.tmp, ocr_file=self.tmp / "ocr.csv")

        self.assertEqual(docs.file_mode, "w")
        self.assertEqual(docs.ocr_docs, [])
        self.assertEqual(docs.tasks, [self.a, self.b])

    def test_init_limit_06(self) -> None:
        """Only the first N tasks are kept when a limit is set."""
        docs = OcrDocs(self.tmp, ocr_file=None, limit=1)

        self.assertEqual(docs.tasks, [self.a])

    def test_init_missing_columns_raises_07(self) -> None:
        """An OCR file without the required columns raises ValueError."""
        ocr_file = self.tmp / "ocr.csv"
        write_csv(ocr_file, ["status", "source"], [["success", "a.png"]])

        with self.assertRaises(ValueError) as ctx:
            OcrDocs(self.tmp, ocr_file=ocr_file)

        self.assertIn("text", str(ctx.exception))

    def test_init_empty_ocr_file_starts_fresh_08(self) -> None:
        """An empty OCR file means nothing is already done."""
        ocr_file = self.tmp / "ocr.csv"
        ocr_file.write_bytes(b"")

        docs = OcrDocs(self.tmp, ocr_file=ocr_file)

        self.assertEqual(docs.file_mode, "w")
        self.assertEqual(docs.ocr_docs, [])
        self.assertEqual(docs.tasks, [self.a, self.b])

    def test_init_corrupt_ocr_file_raises_09(self) -> None:
        """A corrupt file must never be silently overwritten."""
        ocr_file = self.tmp / "ocr.csv"
        ocr_file.write_text('status,source\n"unterminated,2\n', encoding="utf-8")

        with self.assertRaises(ValueError):
            OcrDocs(self.tmp, ocr_file=ocr_file)

    def test_resume_appends_and_skips_successes_10(self) -> None:
        """Images with a successful row are dropped from the tasks."""
        ocr_file = self.tmp / "ocr.csv"
        write_csv(
            ocr_file,
            COLUMNS,
            [
                ["success", str(self.a), "1.0", "ok"],
                ["ERROR", str(self.b), "0.5", "boom"],
            ],
        )

        docs = OcrDocs(self.tmp, ocr_file=ocr_file)

        # Append mode, records kept, only successes count as done
        self.assertEqual(docs.file_mode, "a")
        self.assertEqual(len(docs.ocr_docs), 2)
        # The failed image is scheduled again, the success is not
        self.assertEqual(docs.tasks, [self.b])


if __name__ == "__main__":
    unittest.main()
