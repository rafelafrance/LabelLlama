import unittest

from llama.llm_fields.location.island import Island


class TestIsland(unittest.TestCase):
    def test_island_01(self) -> None:
        """An island named anywhere in the text is kept, whatever its case."""
        assert Island("on long island", "Long Island").island == "Long Island"

    def test_island_02(self) -> None:
        """An island the text never mentions is a hallucination and is dropped."""
        assert Island("on the mainland", "Long Island").island == ""

    def test_island_03(self) -> None:
        """With no text, every value is a hallucination."""
        assert Island("", "Long Island").island == ""
