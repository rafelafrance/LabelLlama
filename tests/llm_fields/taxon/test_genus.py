import unittest

from llama.llm_fields.taxon.genus import Genus


class TestGenus(unittest.TestCase):
    def test_genus_01(self) -> None:
        """Genus names are capitalized."""
        assert Genus("", "canis").genus == "Canis"
        assert Genus("", "CANIS").genus == "Canis"

    def test_genus_02(self) -> None:
        """A properly-cased value is unchanged."""
        assert Genus("", "Canis").genus == "Canis"

    def test_genus_03(self) -> None:
        """Empty input stays empty."""
        assert Genus("", "").genus == ""

    def test_genus_04(self) -> None:
        """Non-string values are converted to strings."""
        assert Genus("", None).genus == ""
        assert Genus("", 123).genus == "123"
