import unittest

from llama.llm_fields.location.utmNorthing import UtmNorthing


class TestUtmNorthing(unittest.TestCase):
    def test_utm_northing_01(self) -> None:
        """A plain number passes through unchanged."""
        assert UtmNorthing("", "4500000").utmNorthing == "4500000"

    def test_utm_northing_02(self) -> None:
        """A leading "N" indicator is removed."""
        assert UtmNorthing("", "N 4500000").utmNorthing == "4500000"

    def test_utm_northing_03(self) -> None:
        """A trailing "N" indicator is removed."""
        assert UtmNorthing("", "4500000 N").utmNorthing == "4500000"

    def test_utm_northing_04(self) -> None:
        """Zero values become an empty string."""
        assert UtmNorthing("", "0").utmNorthing == ""
        assert UtmNorthing("", "0.0").utmNorthing == ""

    def test_utm_northing_05(self) -> None:
        """Empty input stays empty."""
        assert UtmNorthing("", "").utmNorthing == ""
