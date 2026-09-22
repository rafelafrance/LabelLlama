import unittest
from textwrap import dedent

from llama.pylib import fix_ocr


class TestFixOcr(unittest.TestCase):
    # ---------------------------------------------------------------------
    def test_clean_text_01(self) -> None:
        """Stray spaces before punctuation and control characters go."""
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
        actual = fix_ocr.prepare_for_parse(text)
        assert actual == expect

    # ---------------------------------------------------------------------
    def test_remove_identical_lines_02(self) -> None:
        """A repeated identical line is dropped."""
        text = "line 1\nline 2\nline 2\nline 3\n"
        expect = "line 1\nline 2\nline 3"
        actual = fix_ocr.remove_identical_lines(text)
        assert actual == expect

    def test_remove_identical_lines_03(self) -> None:
        """A near-duplicate above the threshold is dropped."""
        text = "line 1\nline 2\nline 1\nline 3\n"
        expect = "line 1\nline 2\nline 1\nline 3"
        actual = fix_ocr.remove_identical_lines(text)
        assert actual == expect

    def test_remove_identical_lines_04(self) -> None:
        """Lines below the similarity threshold all survive."""
        text = "line 1\n \nline 2\n\nline 1\n\nline 3\n"
        expect = "line 1\n\nline 2\n\nline 1\n\nline 3"
        actual = fix_ocr.remove_identical_lines(text)
        assert actual == expect

    # ---------------------------------------------------------------------
    def test_filter_lines_extra_05(self) -> None:
        """Lines containing filter words are removed (case-insensitive), others kept."""
        text = (
            "Department of Botany\nPond near canal\n"
            "Museum of Natural History\nMay 29, 1966"
        )
        expect = "Pond near canal\nMay 29, 1966"
        assert fix_ocr.filter_lines(text) == expect

    def test_filter_lines_extra_06(self) -> None:
        """The pattern is word-bounded: "sciences" does not match "science"."""
        text = "science\nMolecular Sciences"
        expect = "science"
        assert fix_ocr.filter_lines(text) == expect

    def test_filter_lines_extra_07(self) -> None:
        """Blank lines and edge whitespace do not survive."""
        assert fix_ocr.filter_lines("  \nline\n  ") == "line"

    # ---------------------------------------------------------------------
    def test_fix_entities_extra_08(self) -> None:
        """Entities are decoded only with a semicolon, nested ones twice."""
        assert fix_ocr.fix_entities("a<br>b") == "a\nb"
        assert fix_ocr.fix_entities("a<br/>b") == "a\nb"

    def test_fix_entities_extra_09(self) -> None:
        """&amp; is decoded before the other entities."""
        assert fix_ocr.fix_entities("5 &lt; 10 &amp; 3 &gt; 1") == "5 < 10 & 3 > 1"

    def test_fix_entities_extra_10(self) -> None:
        """Decoding happens once, not recursively."""
        assert fix_ocr.fix_entities("&amp;lt;") == "&lt;"

    def test_fix_entities_extra_11(self) -> None:
        """Handle: "<br />" (space before the slash)."""
        assert fix_ocr.fix_entities("a<br />b") == "a\nb"

    # ---------------------------------------------------------------------
    def test_join_lines_extra_12(self) -> None:
        """A single break joins the lines."""
        assert fix_ocr.join_lines("line1\nline2") == "line1 line2"

    def test_join_lines_extra_13(self) -> None:
        """Two or more breaks are kept as a paragraph break."""
        assert fix_ocr.join_lines("line1\n\nline2") == "line1\n\nline2"

    def test_join_lines_extra_14(self) -> None:
        """Extra blank lines collapse to a single paragraph break."""
        assert fix_ocr.join_lines("line1\n\n\nline2") == "line1\n\nline2"

    def test_join_lines_extra_15(self) -> None:
        """Trailing newlines are stripped."""
        assert fix_ocr.join_lines("a\nb\n") == "a b"

    # ---------------------------------------------------------------------
    def test_remove_identical_lines_extra_16(self) -> None:
        """Deduplication is case-sensitive."""
        assert fix_ocr.remove_identical_lines("Line\nline\nx") == "Line\nline\nx"

    def test_remove_identical_lines_extra_17(self) -> None:
        """Space-only lines are kept (as blank lines) and their spaces stripped."""
        assert fix_ocr.remove_identical_lines("a\n   \nb\n   ") == "a\n\nb"

    # ---------------------------------------------------------------------
    def test_clean_ocr_18(self) -> None:
        """A line break tag is turned into a real newline."""
        assert fix_ocr.clean_ocr("a<br>b\na") == "a\nb\na"

    def test_clean_ocr_19(self) -> None:
        """Filter words are kept (filter_lines is not part of clean_ocr)."""
        assert fix_ocr.clean_ocr("Herbarium\nline") == "Herbarium\nline"

    def test_clean_ocr_list_24(self) -> None:
        """clean_ocr only ever passes a string to the cleaner."""
        assert fix_ocr.clean_ocr(["part one", "part two"]) == "part one part two"
        assert fix_ocr.clean_ocr([]) == ""

    # ---------------------------------------------------------------------
    def test_html_to_md_extra_20(self) -> None:
        """Bold / italic markdown notations are stripped."""
        assert fix_ocr.html_to_md("<b>bold</b> and <i>ital</i>") == "bold and ital"
        assert fix_ocr.html_to_md("<b>a</b> and <b>b</b>") == "a and b"

    def test_html_to_md_extra_21(self) -> None:
        """An img tag leaves only the surrounding text."""
        assert fix_ocr.html_to_md('<img src="x.png">hello') == "hello"

    def test_html_to_md_extra_22(self) -> None:
        """Paragraphs are separated by a blank line."""
        assert (
            fix_ocr.html_to_md("<p>para one</p><p>para two</p>")
            == "para one\n\npara two"
        )

    def test_html_to_md_extra_23(self) -> None:
        """Formatting tags are dropped and their text kept."""
        assert fix_ocr.html_to_md("<i>state-wide</i>") == "state-wide"
