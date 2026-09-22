import unittest

from llama.llm_fields.location.decimalLatitude import DecimalLatitude


class TestDecimalLatitude(unittest.TestCase):
    def test_decimal_latitude_01(self) -> None:
        """A numeric string becomes a float."""
        assert DecimalLatitude("", "45.5").decimalLatitude == 45.5

    def test_decimal_latitude_02(self) -> None:
        """A negative latitude keeps its sign."""
        assert DecimalLatitude("", "-1.0").decimalLatitude == -1.0

    def test_decimal_latitude_03(self) -> None:
        """A latitude with no decimal point becomes a whole float."""
        assert DecimalLatitude("", "45").decimalLatitude == 45.0

    def test_decimal_latitude_04(self) -> None:
        """A northern letter before or after the number is ignored."""
        assert DecimalLatitude("", "N45.5").decimalLatitude == 45.5
        assert DecimalLatitude("", "45.5 N").decimalLatitude == 45.5

    def test_decimal_latitude_05(self) -> None:
        """Text that holds no number becomes an empty string."""
        assert DecimalLatitude("", "none").decimalLatitude == ""
        assert DecimalLatitude("", "").decimalLatitude == ""
        assert DecimalLatitude("", "not a number").decimalLatitude == ""

    def test_decimal_latitude_06(self) -> None:
        """Ints, NaN and one-item lists are converted to a latitude."""
        assert DecimalLatitude("", 45).decimalLatitude == 45.0
        assert DecimalLatitude("", float("nan")).decimalLatitude == ""
        assert DecimalLatitude("", [45.5]).decimalLatitude == 45.5

    def test_decimal_latitude_10(self) -> None:
        """A number with more than one decimal point is not a latitude."""
        assert DecimalLatitude("", "45.6.7").decimalLatitude == ""

    def test_decimal_latitude_11(self) -> None:
        """A decimal comma is read as a decimal point."""
        assert DecimalLatitude("", "45,5").decimalLatitude == 45.5

    def test_decimal_latitude_12(self) -> None:
        """A southern letter before or after the number negates it."""
        assert DecimalLatitude("", "S45.5").decimalLatitude == -45.5
        assert DecimalLatitude("", "45.5 S").decimalLatitude == -45.5
        assert DecimalLatitude("", "s 45.5").decimalLatitude == -45.5
        assert DecimalLatitude("", "-45.5 S").decimalLatitude == -45.5
        assert DecimalLatitude("", "45,5 S").decimalLatitude == -45.5

    def test_decimal_latitude_13(self) -> None:
        """A latitude beyond the poles is cleared, the poles are kept."""
        assert DecimalLatitude("", "90").decimalLatitude == 90.0
        assert DecimalLatitude("", "-90").decimalLatitude == -90.0
        assert DecimalLatitude("", "95").decimalLatitude == ""
        assert DecimalLatitude("", "-95").decimalLatitude == ""
        assert DecimalLatitude("", "90.1").decimalLatitude == ""
        assert DecimalLatitude("", "S95").decimalLatitude == ""
