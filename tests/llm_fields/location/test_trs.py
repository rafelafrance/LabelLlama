import unittest

from llama.llm_fields.location.trs import Trs


class TestTrs(unittest.TestCase):
    def test_trs_01(self) -> None:
        """Full TRS string passes through unchanged."""
        assert Trs("", "T3N R4W Sec 12").trs == "T3N R4W Sec 12"

    def test_trs_02(self) -> None:
        """Empty input stays empty."""
        assert Trs("", "").trs == ""

    def test_trs_03(self) -> None:
        """Empty-value notations become an empty string."""
        assert Trs("", "none").trs == ""

    def test_trs_04(self) -> None:
        """Non-string values are converted to strings."""
        assert Trs("", 123).trs == "123"
        assert Trs("", None).trs == ""
