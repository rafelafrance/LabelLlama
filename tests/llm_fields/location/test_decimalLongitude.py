import unittest

from llama.llm_fields.location.decimalLongitude import DecimalLongitude


class TestDecimalLongitude(unittest.TestCase):
    def test_decimal_longitude_01(self) -> None:
        """A negative longitude keeps its sign."""
        assert DecimalLongitude("", "-1.0").decimalLongitude == -1.0

    def test_decimal_longitude_02(self) -> None:
        """A numeric string becomes a float."""
        assert DecimalLongitude("", "-122.5").decimalLongitude == -122.5

    def test_decimal_longitude_03(self) -> None:
        """An eastern letter before or after the number is ignored."""
        assert DecimalLongitude("", "122.5 E").decimalLongitude == 122.5
        assert DecimalLongitude("", "E122.5").decimalLongitude == 122.5

    def test_decimal_longitude_04(self) -> None:
        """Text that holds no number becomes an empty string."""
        assert DecimalLongitude("", "none").decimalLongitude == ""
        assert DecimalLongitude("", "").decimalLongitude == ""

    def test_decimal_longitude_05(self) -> None:
        """An int becomes a float and NaN becomes an empty string."""
        assert DecimalLongitude("", 45).decimalLongitude == 45.0
        assert DecimalLongitude("", float("nan")).decimalLongitude == ""

    def test_decimal_longitude_06(self) -> None:
        """A western letter before or after the number negates it."""
        assert DecimalLongitude("", "W122.5").decimalLongitude == -122.5
        assert DecimalLongitude("", "122.5 W").decimalLongitude == -122.5
        assert DecimalLongitude("", "w 122.5").decimalLongitude == -122.5
        assert DecimalLongitude("", "-122.5 W").decimalLongitude == -122.5
        assert DecimalLongitude("", "122,5 W").decimalLongitude == -122.5

    def test_decimal_longitude_07(self) -> None:
        """A longitude beyond 180 degrees is cleared, 180 is kept."""
        assert DecimalLongitude("", "180").decimalLongitude == 180.0
        assert DecimalLongitude("", "-180").decimalLongitude == -180.0
        assert DecimalLongitude("", "190").decimalLongitude == ""
        assert DecimalLongitude("", "-190").decimalLongitude == ""
        assert DecimalLongitude("", "180.5").decimalLongitude == ""
        assert DecimalLongitude("", "W190").decimalLongitude == ""
