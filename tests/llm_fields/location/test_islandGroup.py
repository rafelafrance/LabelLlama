import unittest

from llama.llm_fields.location.islandGroup import IslandGroup


class TestIslandGroup(unittest.TestCase):
    def test_island_group_01(self) -> None:
        """An island group named anywhere in the text is kept, whatever its case."""
        assert (
            IslandGroup("in the Hawaiian Islands", "Hawaiian Islands").islandGroup
            == "Hawaiian Islands"
        )

    def test_island_group_02(self) -> None:
        """An island group the text never mentions is dropped as a hallucination."""
        assert IslandGroup("on the mainland", "Hawaiian Islands").islandGroup == ""

    def test_island_group_03(self) -> None:
        """With no text, every value is a hallucination."""
        assert IslandGroup("", "Hawaiian Islands").islandGroup == ""
