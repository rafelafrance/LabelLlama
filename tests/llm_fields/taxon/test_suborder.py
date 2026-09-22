import unittest

from llama.llm_fields.taxon.suborder import Suborder


class TestSuborder(unittest.TestCase):
    def test_suborder_01(self) -> None:
        """A value present in the text is kept."""
        assert Suborder("the Violineae suborder", "Violineae").suborder == "Violineae"

    def test_suborder_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert Suborder("the VIOLINEAE suborder", "Violineae").suborder == "Violineae"

    def test_suborder_03(self) -> None:
        """Punctuation is stripped before the hallucination check."""
        assert Suborder("the Violineae suborder", "Violineae,").suborder == "Violineae"

    def test_suborder_04(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert Suborder("some other text", "Violineae").suborder == ""

    def test_suborder_05(self) -> None:
        """An empty value stays empty."""
        assert Suborder("some text", "").suborder == ""
