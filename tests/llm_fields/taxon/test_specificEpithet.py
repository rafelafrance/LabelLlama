import unittest

from llama.llm_fields.taxon.specificEpithet import SpecificEpithet


class TestSpecificEpithet(unittest.TestCase):
    def test_specific_epithet_01(self) -> None:
        """Specific epithets are lower-cased."""
        assert SpecificEpithet("", "latrans").specificEpithet == "latrans"
        assert SpecificEpithet("", "LATRANS").specificEpithet == "latrans"

    def test_specific_epithet_02(self) -> None:
        """Empty input stays empty."""
        assert SpecificEpithet("", "").specificEpithet == ""

    def test_specific_epithet_03(self) -> None:
        """Non-string values are converted to strings."""
        assert SpecificEpithet("", None).specificEpithet == ""
        assert SpecificEpithet("", 123).specificEpithet == "123"
