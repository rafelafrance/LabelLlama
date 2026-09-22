import unittest

from llama.llm_fields.taxon.vernacularName import VernacularName


class TestVernacularName(unittest.TestCase):
    def test_vernacular_name_01(self) -> None:
        """A value present in the text is kept."""
        assert (
            VernacularName("the black bear", "black bear").vernacularName
            == "black bear"
        )

    def test_vernacular_name_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert (
            VernacularName("the BLACK BEAR", "black bear").vernacularName
            == "black bear"
        )

    def test_vernacular_name_03(self) -> None:
        """Punctuation is stripped before the hallucination check."""
        assert (
            VernacularName("the black bear", "black bear,").vernacularName
            == "black bear"
        )

    def test_vernacular_name_04(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert VernacularName("a gray wolf", "black bear").vernacularName == ""

    def test_vernacular_name_05(self) -> None:
        """An empty value stays empty."""
        assert VernacularName("some text", "").vernacularName == ""
