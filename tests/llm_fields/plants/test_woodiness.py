import unittest

from llama.llm_fields.plants.woodiness import Woodiness


class TestWoodiness(unittest.TestCase):
    def test_woodiness_01(self) -> None:
        """A value present in the text is kept."""
        assert Woodiness("the stem is woody", "woody").woodiness == "woody"

    def test_woodiness_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert Woodiness("a HERBACEOUS stem", "herbaceous").woodiness == "herbaceous"

    def test_woodiness_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert Woodiness("the stem is woody", "herbaceous").woodiness == ""

    def test_woodiness_04(self) -> None:
        """An empty value stays empty."""
        assert Woodiness("some text", "").woodiness == ""
