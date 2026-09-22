import unittest

from llama.llm_fields.location.geodeticDatum import GeodeticDatum


class TestGeodeticDatum(unittest.TestCase):
    def test_geodetic_datum_01(self) -> None:
        """Value present in the text is kept."""
        assert GeodeticDatum("WGS84 datum used", "WGS84").geodeticDatum == "WGS84"

    def test_geodetic_datum_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert GeodeticDatum("Nad83", "nad83").geodeticDatum == "nad83"

    def test_geodetic_datum_03(self) -> None:
        """Value not present in the text is a hallucination and becomes empty."""
        assert GeodeticDatum("WGS 84 was used", "NAD83").geodeticDatum == ""

    def test_geodetic_datum_04(self) -> None:
        """Empty text: everything is a hallucination."""
        assert GeodeticDatum("", "WGS84").geodeticDatum == ""
