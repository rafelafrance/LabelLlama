import unittest

from llama.calc_fields.taxon.specificEpithet import SpecificEpithet


class TestSpecificEpithet(unittest.TestCase):
    def test_specific_epithet_01(self) -> None:
        """The epithet is the second word of the scientific name."""
        rec = {"scientificName": "Quercus alba"}
        assert SpecificEpithet(rec, "").specificEpithet == "alba"

    def test_specific_epithet_02(self) -> None:
        """A single-word scientific name has no specific epithet."""
        rec = {"scientificName": "Quercus"}
        assert SpecificEpithet(rec, "").specificEpithet == ""

    def test_specific_epithet_03(self) -> None:
        """A capitalized epithet is lowercased."""
        rec = {"scientificName": "Quercus ALBA"}
        assert SpecificEpithet(rec, "").specificEpithet == "alba"

    def test_specific_epithet_04(self) -> None:
        """Extra words beyond binomial are ignored."""
        rec = {"scientificName": "Quercus alba var. something"}
        assert SpecificEpithet(rec, "").specificEpithet == "alba"

    def test_specific_epithet_05(self) -> None:
        """A record with no scientific name leaves it blank."""
        assert SpecificEpithet({}, "").specificEpithet == ""

    def test_specific_epithet_06(self) -> None:
        """No record at all leaves the epithet blank."""
        assert SpecificEpithet(None, "").specificEpithet == ""

    def test_specific_epithet_07(self) -> None:
        """An existing specific epithet is left untouched."""
        rec = {"scientificName": "Quercus alba"}
        assert SpecificEpithet(rec, "rubra").specificEpithet == "rubra"


if __name__ == "__main__":
    unittest.main()
