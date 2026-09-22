import unittest

from llama.llm_fields.taxon.scientificName import ScientificName


class TestScientificName(unittest.TestCase):
    def test_scientific_name_01(self) -> None:
        """A two-part binomial is normalized: genus capitalized, epithet lower-cased."""
        assert ScientificName("", "Canis latrans").scientificName == "Canis latrans"
        assert ScientificName("", "canis LATRANS").scientificName == "Canis latrans"
        assert ScientificName("", "CANIS LATRANS").scientificName == "Canis latrans"

    def test_scientific_name_02(self) -> None:
        """A single word is capitalized."""
        assert ScientificName("", "canis").scientificName == "Canis"

    def test_scientific_name_03(self) -> None:
        """Punctuation and the authorship citation are removed."""
        assert (
            ScientificName("", "Canis latrans (Erxleb.)").scientificName
            == "Canis latrans"
        )

    def test_scientific_name_04(self) -> None:
        """Only the genus + specific epithet are kept (infraspecific parts dropped)."""
        assert (
            ScientificName("", "Canis latrans familiaris").scientificName
            == "Canis latrans"
        )

    def test_scientific_name_05(self) -> None:
        """Empty input stays empty."""
        assert ScientificName("", "").scientificName == ""
