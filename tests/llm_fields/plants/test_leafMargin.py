import unittest

from llama.llm_fields.plants.leafMargin import LeafMargin


class TestLeafMargin(unittest.TestCase):
    def test_leaf_margin_01(self) -> None:
        """A value present in the text is kept."""
        assert (
            LeafMargin("the leaf margin is serrate", "serrate").leafMargin == "serrate"
        )

    def test_leaf_margin_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert LeafMargin("ENTIRE margins", "entire").leafMargin == "entire"

    def test_leaf_margin_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert LeafMargin("the leaf margin is serrate", "lobed").leafMargin == ""

    def test_leaf_margin_04(self) -> None:
        """An empty value stays empty."""
        assert LeafMargin("some text", "").leafMargin == ""
