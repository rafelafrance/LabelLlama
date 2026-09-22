import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from llama.prompts.field_cleaner import (
    REQUIRED_CLEANER_COLUMNS,
    FieldCleaner,
    format_value,
)
from llama.prompts.prompt import Prompt

DUMMY = Path(__file__).parent / "dummy_prompt.md"
COLUMNS = ["status", "source", "elapsed", "text", "scientificName", "verbatimEventDate"]


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
        self.parsed_file = self.tmp / "parsed.csv"
        write_csv(
            self.parsed_file,
            COLUMNS,
            [
                ["ERROR", "b.txt", "1.0", "text b", "Canis loopy", "10-10-2010"],
                ["success", "a.txt", "1.0", "text a", "Canis loopy", "10-10-2010"],
                ["success", "c.txt", "1.0", "text c", "Canis loopy", "10-10-2010"],
            ],
        )
        self.parsed_file = self.tmp / "parsed.csv"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_init_field_classes_01(self) -> None:
        prompt = make_prompt(DUMMY)
        cleaner = FieldCleaner(prompt, self.parsed_file)

        self.assertEqual(len(cleaner.llm_field_classes), 2)
        self.assertIn("scientificName", cleaner.llm_field_classes)
        self.assertEqual(list(cleaner.calc_field_classes), ["eventDate"])

    def test_validate_columns_ok_02(self) -> None:
        prompt = make_prompt(DUMMY)
        cleaner = FieldCleaner(prompt, self.parsed_file)
        prompt = SimpleNamespace(
            columns=[
                "status",
                "source",
                "elapsed",
                "text",
                "scientificName",
                "verbatimEventDate",
            ]
        )

        # Should not raise when all required and prompt columns are present
        self.assertIsNone(cleaner.validate_columns(list(prompt.columns)))

    def test_validate_columns_missing_required_03(self) -> None:
        prompt = make_prompt(DUMMY)
        cleaner = FieldCleaner(prompt, self.parsed_file)
        prompt = SimpleNamespace(columns=[*REQUIRED_CLEANER_COLUMNS, "scientificName"])

        with self.assertRaises(ValueError) as ctx:
            cleaner.validate_columns(["status", "source"])

        msg = str(ctx.exception)
        self.assertIn("required", msg)
        self.assertIn("text", msg)

    def test_validate_columns_missing_prompt_columns_04(self) -> None:
        prompt = make_prompt(DUMMY)
        cleaner = FieldCleaner(prompt, self.parsed_file)
        prompt = SimpleNamespace(
            columns=["status", "source", "elapsed", "text", "scientificName"]
        )

        with self.assertRaises(ValueError) as ctx:
            cleaner.validate_columns(["status", "source", "elapsed", "text"])

        msg = str(ctx.exception)
        self.assertIn("prompt columns", msg)
        self.assertIn("scientificName", msg)

    def test_get_llm_columns_05(self) -> None:
        prompt = make_prompt(DUMMY)
        cleaner = FieldCleaner(prompt, self.parsed_file)

        self.assertEqual(cleaner.llm_columns, ["scientificName", "verbatimEventDate"])

    def test_get_calc_columns_06(self) -> None:
        prompt = make_prompt(DUMMY)
        cleaner = FieldCleaner(prompt, self.parsed_file)

        self.assertEqual(cleaner.calc_columns, ["eventDate"])

    def test_get_output_columns_07(self) -> None:
        prompt = make_prompt(DUMMY)
        cleaner = FieldCleaner(prompt, self.parsed_file)
        columns = cleaner.get_output_columns()

        self.assertEqual(columns[:2], ["source", "text"])
        self.assertIn("scientificName", columns)
        self.assertIn("eventDate", columns)
        # No duplicates, and no parse-only columns leak in
        self.assertEqual(len(columns), len(set(columns)))
        self.assertNotIn("status", columns)
        self.assertNotIn("elapsed", columns)

    def test_format_bools_are_spelled_like_gold_08(self) -> None:
        # gold_std spells booleans TRUE/FALSE, and str() gives True/False
        self.assertEqual(format_value(value=True), "TRUE")
        self.assertEqual(format_value(value=False), "FALSE")

    def test_format_whole_floats_have_no_dot_zero_09(self) -> None:
        # Calc fields hand us floats: 1000 m is "1000", a unit conversion keeps
        # its decimals
        self.assertEqual(format_value(1000.0), "1000")
        self.assertEqual(format_value(-484145.0), "-484145")
        self.assertEqual(format_value(0.0), "0")
        self.assertEqual(format_value(914.4), "914.4")
        self.assertEqual(format_value(37), "37")

    def test_format_float_noise_is_trimmed_10(self) -> None:
        # 3000 feet is 914.4 metres, not 914.4000000000001
        self.assertEqual(format_value(914.4000000000001), "914.4")
        self.assertEqual(format_value(0.1 + 0.2), "0.3")
        # ... without eating the digits of a real coordinate
        self.assertEqual(format_value(-71.4123456789), "-71.4123456789")

    def test_format_missing_is_blank_11(self) -> None:
        self.assertEqual(format_value(None), "")
        self.assertEqual(format_value(float("nan")), "")
        self.assertEqual(format_value(pd.NA), "")
        self.assertEqual(format_value(pd.NaT), "")
        self.assertEqual(format_value(np.nan), "")

    def test_format_strings_pass_through_12(self) -> None:
        self.assertEqual(format_value("Iris virginica"), "Iris virginica")
        self.assertEqual(format_value(""), "")
        self.assertEqual(format_value("NA"), "NA")

    def test_format_sequence_does_not_raise_13(self) -> None:
        # pd.isna() of a list is not a scalar, so it must not be tested as one
        self.assertEqual(format_value(["a", "b"]), "['a', 'b']")
        self.assertEqual(format_value(np.array([1.0, 2.0])), "[1. 2.]")


if __name__ == "__main__":
    unittest.main()
