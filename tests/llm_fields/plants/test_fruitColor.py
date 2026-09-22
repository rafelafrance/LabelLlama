import unittest

from llama.llm_fields.plants.fruitColor import FruitColor


class TestFruitColor(unittest.TestCase):
    def test_fruit_color_01(self) -> None:
        """A value present in the text is kept."""
        assert FruitColor("the fruit is blue", "blue").fruitColor == "blue"

    def test_fruit_color_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert FruitColor("the fruit is PURPLE", "Purple").fruitColor == "Purple"

    def test_fruit_color_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert FruitColor("the fruit is blue", "red").fruitColor == ""

    def test_fruit_color_04(self) -> None:
        """An empty value stays empty."""
        assert FruitColor("some text", "").fruitColor == ""

    def test_fruit_color_05(self) -> None:
        """Trailing punctuation is removed once the value is matched in the text."""
        assert FruitColor("the fruit is blue.", "blue.").fruitColor == "blue"

    def test_fruit_color_bug_06(self) -> None:
        """Trailing punctuation is stripped from the colour."""
        assert FruitColor("the fruit is blue", "blue,").fruitColor == "blue"
