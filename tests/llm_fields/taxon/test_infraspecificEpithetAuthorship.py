import unittest

from llama.llm_fields.taxon.infraspecificEpithetAuthorship import (
    InfraspecificEpithetAuthorship,
)


class TestInfraspecificEpithetAuthorship(unittest.TestCase):
    def test_infraspecific_epithet_authorship_01(self) -> None:
        """A plain authorship passes through unchanged."""
        assert (
            InfraspecificEpithetAuthorship("", "Miller").infraspecificEpithetAuthorship
            == "Miller"
        )

    def test_infraspecific_epithet_authorship_02(self) -> None:
        """Surrounding whitespace is stripped; internal content is preserved."""
        assert (
            InfraspecificEpithetAuthorship(
                "", "  Smith, 1753  "
            ).infraspecificEpithetAuthorship
            == "Smith, 1753"
        )

    def test_infraspecific_epithet_authorship_03(self) -> None:
        """Surrounding brackets are removed."""
        assert (
            InfraspecificEpithetAuthorship("", "(Smith)").infraspecificEpithetAuthorship
            == "Smith"
        )

    def test_infraspecific_epithet_authorship_04(self) -> None:
        """Internal balanced authorship parentheses are preserved."""
        assert (
            InfraspecificEpithetAuthorship(
                "", "Smith (1753)."
            ).infraspecificEpithetAuthorship
            == "Smith (1753)"
        )

    def test_infraspecific_epithet_authorship_05(self) -> None:
        """Empty input stays empty."""
        assert (
            InfraspecificEpithetAuthorship("", "").infraspecificEpithetAuthorship == ""
        )
