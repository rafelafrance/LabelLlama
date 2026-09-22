import unittest

from llama.llm_fields.taxon.infraspecificEpithet import InfraspecificEpithet


class TestInfraspecificEpithet(unittest.TestCase):
    def test_infraspecific_epithet_01(self) -> None:
        """Infraspecific epithets are lower-cased."""
        assert InfraspecificEpithet("", "novae").infraspecificEpithet == "novae"
        assert InfraspecificEpithet("", "NOVAE").infraspecificEpithet == "novae"

    def test_infraspecific_epithet_02(self) -> None:
        """Empty input stays empty."""
        assert InfraspecificEpithet("", "").infraspecificEpithet == ""

    def test_infraspecific_epithet_03(self) -> None:
        """Non-string values are converted to strings."""
        assert InfraspecificEpithet("", None).infraspecificEpithet == ""
