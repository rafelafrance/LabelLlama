import unittest

from llama.llm_fields.location.municipality import Municipality


class TestMunicipality(unittest.TestCase):
    def test_municipality_01(self) -> None:
        """Value present in the text is kept (case-insensitive)."""
        assert Municipality("near victoria town", "Victoria").municipality == "Victoria"

    def test_municipality_02(self) -> None:
        """Value not present in the text is a hallucination and becomes empty."""
        assert Municipality("near the coast", "Victoria").municipality == ""

    def test_municipality_03(self) -> None:
        """Empty text: everything is a hallucination."""
        assert Municipality("", "Victoria").municipality == ""
