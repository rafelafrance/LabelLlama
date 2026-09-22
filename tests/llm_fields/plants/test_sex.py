import unittest

from llama.llm_fields.plants.sex import Sex


class TestSex(unittest.TestCase):
    def test_sex_01(self) -> None:
        """A value present in the text is kept."""
        assert Sex("a male flower", "male").sex == "male"

    def test_sex_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert Sex("a FEMALE inflorescence", "female").sex == "female"

    def test_sex_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert Sex("a male flower", "female").sex == ""

    def test_sex_04(self) -> None:
        """An empty value stays empty."""
        assert Sex("some text", "").sex == ""
