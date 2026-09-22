import unittest

from llama.calc_fields.location.country import Country


class TestCountry(unittest.TestCase):
    def test_country_01(self) -> None:
        """A US state name fills a blank country with United States."""
        rec = {"stateProvince": "Texas"}
        assert Country(rec, "").country == "United States"

    def test_country_02(self) -> None:
        """A US county name fills a blank country with United States."""
        rec = {"county": "Kitsap"}
        assert Country(rec, "").country == "United States"

    def test_country_03(self) -> None:
        """A province outside the United States leaves it blank."""
        rec = {"stateProvince": "Ontario"}
        assert Country(rec, "").country == ""

    def test_country_04(self) -> None:
        """A county outside the United States leaves it blank."""
        rec = {"county": "Kildare"}
        assert Country(rec, "").country == ""

    def test_country_05(self) -> None:
        """A country written on the label is never overwritten."""
        assert Country({"stateProvince": "Texas"}, "Canada").country == "Canada"

    def test_country_06(self) -> None:
        """A country spelling in the vocabulary is standardised."""
        assert Country({}, "usa").country == "USA"

    def test_country_07(self) -> None:
        """The vocabulary lookup for a country ignores case."""
        assert Country({}, "U.S.A.").country == "USA"


if __name__ == "__main__":
    unittest.main()
