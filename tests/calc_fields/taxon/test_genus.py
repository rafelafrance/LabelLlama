import unittest

from llama.calc_fields.taxon.genus import Genus


class TestGenus(unittest.TestCase):
    def test_genus_01(self) -> None:
        """The genus is the first word of the scientific name."""
        rec = {"scientificName": "Quercus alba"}
        assert Genus(rec, "").genus == "Quercus"

    def test_genus_02(self) -> None:
        """A single-word scientific name is the genus."""
        rec = {"scientificName": "Quercus"}
        assert Genus(rec, "").genus == "Quercus"

    def test_genus_03(self) -> None:
        """A lowercase genus is capitalized."""
        rec = {"scientificName": "quercus alba"}
        assert Genus(rec, "").genus == "Quercus"

    def test_genus_04(self) -> None:
        """A record with no scientific name leaves it blank."""
        assert Genus({}, "").genus == ""

    def test_genus_05(self) -> None:
        """No record at all leaves the genus blank."""
        assert Genus(None, "").genus == ""

    def test_genus_06(self) -> None:
        """An existing genus is left untouched."""
        rec = {"scientificName": "Quercus alba"}
        assert Genus(rec, "Pinus").genus == "Pinus"


if __name__ == "__main__":
    unittest.main()
