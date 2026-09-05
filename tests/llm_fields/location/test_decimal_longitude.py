import unittest

from llama.llm_fields.location.decimalLongitude import DecimalLongitude


class TestDecimalLongitude(unittest.TestCase):
    def test_decimal_longitude_01(self) -> None:
        assert DecimalLongitude("", "-1.0").decimalLongitude == -1.0
