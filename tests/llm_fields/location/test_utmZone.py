import unittest

from llama.llm_fields.location.utmZone import UtmZone


class TestUtmZone(unittest.TestCase):
    def test_utm_zone_01(self) -> None:
        """A plain zone passes through unchanged."""
        assert UtmZone("", "17N").utmZone == "17N"

    def test_utm_zone_02(self) -> None:
        """The "zone" label is removed."""
        assert UtmZone("", "zone 17N").utmZone == "17N"

    def test_utm_zone_03(self) -> None:
        """The "z" label is removed."""
        assert UtmZone("", "z 17N").utmZone == "17N"

    def test_utm_zone_04(self) -> None:
        """The "z." label is removed."""
        assert UtmZone("", "z. 17N").utmZone == "17N"

    def test_utm_zone_05(self) -> None:
        """Empty input stays empty."""
        assert UtmZone("", "").utmZone == ""

    def test_utm_zone_10(self) -> None:
        """An upper case zone label is removed."""
        assert UtmZone("", "Zone 17N").utmZone == "17N"
