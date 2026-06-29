import unittest
from textwrap import dedent

from llama.pylib import fix_ocr


class TestFixOcr(unittest.TestCase):
    # ---------------------------------------------------------------------
    def test_clean_text_01(self) -> None:
        text = dedent("""
            HERBARIUM
            F. H. SARGENT
            Paspalum urvillei Steud.
            Locality
            Picayune, Miss.
            Habitat
            Waste ground.
            Date
            May 29, 1966.
            """)
        expect = (
            "F. H. SARGENT Paspalum urvillei Steud. Locality Picayune, Miss. "
            "Habitat Waste ground. Date May 29, 1966."
        )
        actual = fix_ocr.clean_text(text)
        assert actual == expect

    # ---------------------------------------------------------------------
    def test_remove_identical_lines_01(self) -> None:
        text = "line 1\nline 2\nline 2\nline 3\n"
        expect = "line 1\nline 2\nline 3"
        actual = fix_ocr.remove_identical_lines(text)
        assert actual == expect

    def test_remove_identical_lines_02(self) -> None:
        text = "line 1\nline 2\nline 1\nline 3\n"
        expect = "line 1\nline 2\nline 3"
        actual = fix_ocr.remove_identical_lines(text)
        assert actual == expect

    def test_remove_identical_lines_03(self) -> None:
        text = "line 1\n \nline 2\n\nline 1\n\nline 3\n"
        expect = "line 1\n\nline 2\n\n\nline 3"
        actual = fix_ocr.remove_identical_lines(text)
        assert actual == expect
