import unittest

from llama.llm_fields.location.trsTownship import TrsTownship


class TestTrsTownship(unittest.TestCase):
    def test_trs_township_01(self) -> None:
        """The "t" label is removed."""
        assert TrsTownship("", "t 3").trsTownship == "3"

    def test_trs_township_02(self) -> None:
        """Label removal is case-insensitive."""
        assert TrsTownship("", "T 3").trsTownship == "3"

    def test_trs_township_03(self) -> None:
        """The label is removed even with no separating space."""
        assert TrsTownship("", "t3").trsTownship == "3"

    def test_trs_township_04(self) -> None:
        """A value without a label is unchanged."""
        assert TrsTownship("", "3").trsTownship == "3"

    def test_trs_township_05(self) -> None:
        """Empty inputs and empty-value notations stay empty."""
        assert TrsTownship("", "").trsTownship == ""
        assert TrsTownship("", "none").trsTownship == ""

    def test_trs_township_10(self) -> None:
        """The whole word township is a label."""
        assert TrsTownship("", "township 3").trsTownship == "3"

    def test_trs_township_11(self) -> None:
        """The dot after the label does not stop the match."""
        assert TrsTownship("", "T. 3").trsTownship == "3"
