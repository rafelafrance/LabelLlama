import unittest

from llama.llm_fields.plants.flowerColor import FlowerColor


class TestFlowerColor(unittest.TestCase):
    def test_flower_color_01(self) -> None:
        """A value present in the text is kept."""
        assert FlowerColor("the flowers are red", "red").flowerColor == "red"

    def test_flower_color_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert FlowerColor("the flowers are RED", "Red").flowerColor == "Red"

    def test_flower_color_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert FlowerColor("the flowers are white", "red").flowerColor == ""

    def test_flower_color_04(self) -> None:
        """An empty value stays empty."""
        assert FlowerColor("some text", "").flowerColor == ""

    def test_flower_color_05(self) -> None:
        """Trailing punctuation is removed once the value is matched in the text."""
        assert FlowerColor("the flowers are red.", "red.").flowerColor == "red"

    def test_flower_color_bug_06(self) -> None:
        """Trailing punctuation is removed."""
        assert FlowerColor("the flowers are red", "red,").flowerColor == "red"

    def test_flower_color_bug_07(self) -> None:
        """Trailing punctuation is stripped from the colour."""
        assert FlowerColor("the flowers are red", "red.").flowerColor == "red"
