import unittest

from llama.llm_fields.location.country import Country


class TestCountry(unittest.TestCase):
    def test_country_01(self) -> None:
        """A country name is title-cased."""
        assert Country("", "united states").country == "United States"

    def test_country_02(self) -> None:
        """Small words are lowercased unless they start the name."""
        assert Country("", "island of man").country == "Island of Man"
        assert Country("", "the netherlands").country == "The Netherlands"

    def test_country_03(self) -> None:
        """A value that is already title-cased is unchanged."""
        assert Country("", "United States").country == "United States"

    def test_country_04(self) -> None:
        """An empty value stays empty."""
        assert Country("", "").country == ""

    def test_country_10(self) -> None:
        """A None value becomes an empty string."""
        assert Country("", None).country == ""

    def test_country_11(self) -> None:
        """The word "none" counts as an empty field."""
        assert Country("", "none").country == ""

    def test_country_12(self) -> None:
        """Periods and apostrophes inside a name survive the title-casing."""
        assert Country("", "st. john's").country == "St. John's"
