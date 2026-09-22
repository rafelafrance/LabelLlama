import unittest

from llama.llm_fields.location.trsSection import TrsSection


class TestTrsSection(unittest.TestCase):
    def test_trs_section_01(self) -> None:
        """The "s" label is removed."""
        assert TrsSection("", "s 12").trsSection == "12"

    def test_trs_section_02(self) -> None:
        """A value without a label is unchanged."""
        assert TrsSection("", "12").trsSection == "12"

    def test_trs_section_03(self) -> None:
        """Empty inputs and empty-value notations stay empty."""
        assert TrsSection("", "").trsSection == ""
        assert TrsSection("", "none").trsSection == ""

    def test_trs_section_10(self) -> None:
        """Various forms of the word section."""
        assert TrsSection("", "sec 12").trsSection == "12"
        assert TrsSection("", "Section 12").trsSection == "12"

    def test_trs_section_11(self) -> None:
        """An upper case label is removed too."""
        assert TrsSection("", "S 12").trsSection == "12"

    def test_trs_section_12(self) -> None:
        """The dot after the label does not stop the match."""
        assert TrsSection("", "s. 12").trsSection == "12"
