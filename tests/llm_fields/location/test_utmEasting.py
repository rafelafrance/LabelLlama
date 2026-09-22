import unittest

from llama.llm_fields.location.utmEasting import UtmEasting


class TestUtmEasting(unittest.TestCase):
    def test_utm_easting_01(self) -> None:
        """A plain number passes through unchanged."""
        assert UtmEasting("", "500000").utmEasting == "500000"

    def test_utm_easting_02(self) -> None:
        """A leading "E" indicator is removed."""
        assert UtmEasting("", "E 500000").utmEasting == "500000"

    def test_utm_easting_03(self) -> None:
        """A trailing "E" indicator is removed."""
        assert UtmEasting("", "500000 E").utmEasting == "500000"

    def test_utm_easting_04(self) -> None:
        """Zero values become an empty string."""
        assert UtmEasting("", "0").utmEasting == ""
        assert UtmEasting("", "0.0").utmEasting == ""

    def test_utm_easting_05(self) -> None:
        """Empty input stays empty."""
        assert UtmEasting("", "").utmEasting == ""
