import unittest

from llama.llm_fields.location.utm import Utm


class TestUtm(unittest.TestCase):
    def test_utm_01(self) -> None:
        """The complete coordinate string passes through unchanged."""
        assert Utm("", "17N 500000 4500000").utm == "17N 500000 4500000"

    def test_utm_02(self) -> None:
        """Empty input stays empty."""
        assert Utm("", "").utm == ""

    def test_utm_03(self) -> None:
        """Empty-value notations become an empty string."""
        assert Utm("", "none").utm == ""

    def test_utm_04(self) -> None:
        """Non-string values are converted to strings."""
        assert Utm("", 123).utm == "123"
        assert Utm("", None).utm == ""
