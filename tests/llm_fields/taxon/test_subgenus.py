import unittest

from llama.llm_fields.taxon.subgenus import Subgenus


class TestSubgenus(unittest.TestCase):
    def test_subgenus_01(self) -> None:
        """A value present in the text is kept."""
        assert Subgenus("a Caninae group", "Caninae").subgenus == "Caninae"

    def test_subgenus_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert Subgenus("a CANINAE group", "Caninae").subgenus == "Caninae"

    def test_subgenus_03(self) -> None:
        """Punctuation is stripped before the hallucination check."""
        assert Subgenus("a Caninae group", "Caninae,").subgenus == "Caninae"

    def test_subgenus_04(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert Subgenus("some other text", "Caninae").subgenus == ""

    def test_subgenus_05(self) -> None:
        """An empty value stays empty."""
        assert Subgenus("some text", "").subgenus == ""
