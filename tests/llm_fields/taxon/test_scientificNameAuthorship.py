import unittest

from llama.llm_fields.taxon.scientificNameAuthorship import ScientificNameAuthorship


class TestScientificNameAuthorship(unittest.TestCase):
    def test_scientific_name_authorship_01(self) -> None:
        """A plain authorship passes through unchanged."""
        assert (
            ScientificNameAuthorship("", "Miller").scientificNameAuthorship == "Miller"
        )

    def test_scientific_name_authorship_02(self) -> None:
        """Surrounding whitespace is stripped; internal content is preserved."""
        assert (
            ScientificNameAuthorship("", "  Smith, 1753  ").scientificNameAuthorship
            == "Smith, 1753"
        )

    def test_scientific_name_authorship_03(self) -> None:
        """Surrounding brackets are removed."""
        assert (
            ScientificNameAuthorship("", "(Smith)").scientificNameAuthorship == "Smith"
        )
        assert (
            ScientificNameAuthorship("", "(Smith, 1753)").scientificNameAuthorship
            == "Smith, 1753"
        )

    def test_scientific_name_authorship_04(self) -> None:
        """Internal balanced authorship parentheses are preserved."""
        assert (
            ScientificNameAuthorship("", "Smith (1753).").scientificNameAuthorship
            == "Smith (1753)"
        )

    def test_scientific_name_authorship_05(self) -> None:
        """Empty input stays empty."""
        assert ScientificNameAuthorship("", "").scientificNameAuthorship == ""
