import unittest

from llama.llm_fields.location.trsRange import TrsRange


class TestTrsRange(unittest.TestCase):
    def test_trs_range_01(self) -> None:
        """The "r" label is removed."""
        assert TrsRange("", "r 4").trsRange == "4"

    def test_trs_range_02(self) -> None:
        """Label removal is case-insensitive."""
        assert TrsRange("", "R 4").trsRange == "4"

    def test_trs_range_03(self) -> None:
        """The label is removed even with no separating space."""
        assert TrsRange("", "r4").trsRange == "4"

    def test_trs_range_04(self) -> None:
        """A value without a label is unchanged."""
        assert TrsRange("", "4").trsRange == "4"

    def test_trs_range_05(self) -> None:
        """Empty inputs and empty-value notations stay empty."""
        assert TrsRange("", "").trsRange == ""
        assert TrsRange("", "none").trsRange == ""

    def test_trs_range_10(self) -> None:
        """The whole word 'range' counts as the label too."""
        assert TrsRange("", "range 4").trsRange == "4"

    def test_trs_range_11(self) -> None:
        """An upper case 'R.' abbreviation is removed."""
        assert TrsRange("", "R. 4").trsRange == "4"
