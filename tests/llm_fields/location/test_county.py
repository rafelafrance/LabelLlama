import unittest

from llama.llm_fields.location.county import County


class TestCounty(unittest.TestCase):
    def test_county_01(self) -> None:
        """A trailing "County" label is dropped from the name."""
        assert County("", "Cameron County").county == "Cameron"

    def test_county_02(self) -> None:
        """The "Co." abbreviation is dropped too, in any case."""
        assert County("", "Cameron Co.").county == "Cameron"
        assert County("", "Cameron co").county == "Cameron"

    def test_county_03(self) -> None:
        """The label is dropped only when it is the last word."""
        assert County("", "Cameron County, Texas").county == "Cameron County, Texas"

    def test_county_04(self) -> None:
        """Letters inside a name are not mistaken for the label."""
        assert County("", "Canyon").county == "Canyon"
        assert County("", "Cameronco").county == "Cameronco"

    def test_county_05(self) -> None:
        """An empty value and the word "none" both stay empty."""
        assert County("", "").county == ""
        assert County("", "none").county == ""
