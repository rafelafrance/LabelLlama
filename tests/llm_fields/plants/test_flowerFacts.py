import unittest

from llama.llm_fields.plants.flowerFacts import FlowerFacts


class TestFlowerFacts(unittest.TestCase):
    def test_flower_facts_01(self) -> None:
        """A single string passes through unchanged."""
        assert FlowerFacts("", "fragrant").flowerFacts == "fragrant"

    def test_flower_facts_02(self) -> None:
        """A single-item list reduces to that item."""
        assert FlowerFacts("", ["white"]).flowerFacts == "white"

    def test_flower_facts_03(self) -> None:
        """Multiple items are reduced to the list's string form."""
        assert FlowerFacts("", ["white", "scented"]).flowerFacts == "white, scented"

    def test_flower_facts_04(self) -> None:
        """Empty input becomes an empty string."""
        assert FlowerFacts("", "").flowerFacts == ""
        assert FlowerFacts("", []).flowerFacts == ""

    def test_flower_facts_05(self) -> None:
        """Non-string values are converted to strings."""
        assert FlowerFacts("", 5).flowerFacts == "5"

    def test_flower_facts_06(self) -> None:
        """Empty items within a list are dropped."""
        assert FlowerFacts("", ["white", "", "scented"]).flowerFacts == "white, scented"
