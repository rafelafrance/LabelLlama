import unittest

from llama.llm_fields.plants.leafDuration import LeafDuration


class TestLeafDuration(unittest.TestCase):
    def test_leaf_duration_01(self) -> None:
        """A value present in the text is kept."""
        assert (
            LeafDuration("the foliage is evergreen", "evergreen").leafDuration
            == "evergreen"
        )

    def test_leaf_duration_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert (
            LeafDuration("DECIDUOUS in autumn", "deciduous").leafDuration == "deciduous"
        )

    def test_leaf_duration_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert LeafDuration("the foliage is evergreen", "deciduous").leafDuration == ""

    def test_leaf_duration_04(self) -> None:
        """An empty value stays empty."""
        assert LeafDuration("some text", "").leafDuration == ""
