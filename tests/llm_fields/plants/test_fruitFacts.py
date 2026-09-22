import unittest

from llama.llm_fields.plants.fruitFacts import FruitFacts


class TestFruitFacts(unittest.TestCase):
    def test_fruit_facts_01(self) -> None:
        """A single string passes through unchanged."""
        assert FruitFacts("", "edible").fruitFacts == "edible"

    def test_fruit_facts_02(self) -> None:
        """A single-item list reduces to that item."""
        assert FruitFacts("", ["round"]).fruitFacts == "round"

    def test_fruit_facts_03(self) -> None:
        """Multiple items are reduced to the list's string form."""
        assert FruitFacts("", ["red", "round"]).fruitFacts == "red, round"

    def test_fruit_facts_04(self) -> None:
        """Empty input becomes an empty string."""
        assert FruitFacts("", "").fruitFacts == ""
        assert FruitFacts("", []).fruitFacts == ""

    def test_fruit_facts_05(self) -> None:
        """Non-string values are converted to strings."""
        assert FruitFacts("", 3).fruitFacts == "3"
