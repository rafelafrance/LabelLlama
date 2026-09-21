import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from llama.prompts.field_cleaner import REQUIRED_COLUMNS, FieldCleaner
from llama.prompts.prompt import Prompt

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"
DIODE = PROMPTS_DIR / "diode_one_v1.md"
COLUMNS = ["status", "source", "elapsed", "text"]


def make_prompt(path: Path, **kwargs: dict) -> Prompt:
    kwargs.setdefault("model_id", "test-model")
    return Prompt(prompt_md=path, **kwargs)


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


class TestFieldCleaner(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

        # Sources are deliberately out of order
        self.ocr_file = self.tmp / "ocr.csv"
        write_csv(
            self.ocr_file,
            COLUMNS,
            [
                ["ERROR", "b.txt", "1.0", "text b"],
                ["success", "a.txt", "1.0", "text a"],
                ["success", "c.txt", "1.0", "text c"],
            ],
        )
        self.parsed_file = self.tmp / "parsed.csv"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_init_field_classes_01(self) -> None:
        prompt = make_prompt(DIODE)
        cleaner = FieldCleaner(prompt, self.parsed_file)

        self.assertEqual(len(cleaner.llm_field_classes), 25)
        self.assertIn("scientificName", cleaner.llm_field_classes)
        self.assertEqual(
            list(cleaner.calc_field_classes),
            ["eventDate", "country", "locality"],
        )

    def test_validate_columns_ok_02(self) -> None:
        prompt = make_prompt(DIODE)
        cleaner = FieldCleaner(prompt, self.parsed_file)
        prompt = SimpleNamespace(
            columns=["status", "source", "elapsed", "text", "scientificName"]
        )

        # Should not raise when all required and prompt columns are present
        self.assertIsNone(cleaner.validate_columns(list(prompt.columns), prompt))

    def test_validate_columns_missing_required_03(self) -> None:
        prompt = make_prompt(DIODE)
        cleaner = FieldCleaner(prompt, self.parsed_file)
        prompt = SimpleNamespace(columns=[*REQUIRED_COLUMNS, "scientificName"])

        with self.assertRaises(ValueError) as ctx:
            cleaner.validate_columns(["status", "source"], prompt)

        msg = str(ctx.exception)
        self.assertIn("required", msg)
        self.assertIn("text", msg)

    def test_validate_columns_missing_prompt_columns_04(self) -> None:
        prompt = make_prompt(DIODE)
        cleaner = FieldCleaner(prompt, self.parsed_file)
        prompt = SimpleNamespace(
            columns=["status", "source", "elapsed", "text", "scientificName"]
        )

        with self.assertRaises(ValueError) as ctx:
            cleaner.validate_columns(["status", "source", "elapsed", "text"], prompt)

        msg = str(ctx.exception)
        self.assertIn("prompt columns", msg)
        self.assertIn("scientificName", msg)

    def test_get_llm_columns_05(self) -> None:
        prompt = make_prompt(DIODE)
        cleaner = FieldCleaner(prompt, self.parsed_file)

        columns = [
            "status",
            "source",
            "catalogNumber",
            "scientificName",
            "extra",
        ]
        self.assertEqual(
            cleaner.get_llm_columns(columns),
            ["catalogNumber", "scientificName"],
        )

    def test_get_calc_columns_06(self) -> None:
        prompt = make_prompt(DIODE)
        cleaner = FieldCleaner(prompt, self.parsed_file)

        self.assertEqual(
            cleaner.get_calc_columns(), ["eventDate", "country", "locality"]
        )

    def test_get_output_columns_07(self) -> None:
        prompt = make_prompt(DIODE)
        cleaner = FieldCleaner(prompt, self.parsed_file)
        columns = cleaner.get_output_columns()

        self.assertEqual(columns[:2], ["source", "text"])
        self.assertIn("scientificName", columns)
        self.assertIn("eventDate", columns)
        # No duplicates, and no parse-only columns leak in
        self.assertEqual(len(columns), len(set(columns)))
        self.assertNotIn("status", columns)
        self.assertNotIn("elapsed", columns)


if __name__ == "__main__":
    unittest.main()
