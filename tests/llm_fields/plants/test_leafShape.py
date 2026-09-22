import unittest

from llama.llm_fields.plants.leafShape import LeafShape


class TestLeafShape(unittest.TestCase):
    def test_leaf_shape_01(self) -> None:
        """A value present in the text is kept."""
        assert LeafShape("the leaves are ovate", "ovate").leafShape == "ovate"

    def test_leaf_shape_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert LeafShape("LANCEOLATE leaves", "lanceolate").leafShape == "lanceolate"

    def test_leaf_shape_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert LeafShape("the leaves are ovate", "orbicular").leafShape == ""

    def test_leaf_shape_04(self) -> None:
        """An empty value stays empty."""
        assert LeafShape("some text", "").leafShape == ""
