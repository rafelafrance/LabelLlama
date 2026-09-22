import unittest

from llama.llm_fields.plants.abundance import Abundance


class TestAbundance(unittest.TestCase):
    def test_abundance_01(self) -> None:
        """A value present in the text is kept."""
        assert Abundance("it is common here", "common").abundance == "common"

    def test_abundance_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert Abundance("the plant is RARE", "rare").abundance == "rare"

    def test_abundance_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert Abundance("it is common here", "abundant").abundance == ""

    def test_abundance_04(self) -> None:
        """An empty value stays empty."""
        assert Abundance("some text", "").abundance == ""

    def test_abundance_05(self) -> None:
        """Trailing punctuation is removed once the value is matched in the text."""
        assert Abundance("it is common.", "common.").abundance == "common"

    def test_abundance_06(self) -> None:
        """Trailing punctuation is stripped AFTER the hallucination."""
        assert Abundance("it is common here", "common,").abundance == "common"
