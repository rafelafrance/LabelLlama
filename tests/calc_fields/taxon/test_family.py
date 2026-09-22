import unittest

from llama.calc_fields.taxon.family import Family


class TestFamily(unittest.TestCase):
    def test_family_01(self) -> None:
        """The family is looked up from the scientific name."""
        rec = {"scientificName": "Quercus alba"}
        assert Family(rec, "").family == "Fagaceae"

    def test_family_02(self) -> None:
        """A single-word scientific name (genus only) still yields a family."""
        rec = {"scientificName": "Quercus"}
        assert Family(rec, "").family == "Fagaceae"

    def test_family_03(self) -> None:
        """Unknown genus leaves the family blank."""
        rec = {"scientificName": "Zzzzunknownia alba"}
        assert Family(rec, "").family == ""

    def test_family_04(self) -> None:
        """A record with no scientific name leaves it blank."""
        assert Family({}, "").family == ""

    def test_family_05(self) -> None:
        """No record at all leaves the family blank."""
        assert Family(None, "").family == ""

    def test_family_06(self) -> None:
        """An existing family is left untouched."""
        rec = {"scientificName": "Quercus alba"}
        assert Family(rec, "Pinaceae").family == "Pinaceae"

    def test_family_07(self) -> None:
        """Scoring: expect is empty and actual matches the genus' family."""
        record = {"scientificName": "Quercus alba"}
        assert Family.score("", "Fagaceae", record) == 1.0

    def test_family_08(self) -> None:
        """Scoring: expect is empty but actual does not match the genus' family."""
        record = {"scientificName": "Quercus alba"}
        assert Family.score("", "Pinaceae", record) < 1.0

    def test_family_09(self) -> None:
        """Scoring: identical non-empty values score 1.0."""
        record = {"scientificName": "Quercus alba"}
        assert Family.score("Fagaceae", "Fagaceae", record) == 1.0


if __name__ == "__main__":
    unittest.main()
