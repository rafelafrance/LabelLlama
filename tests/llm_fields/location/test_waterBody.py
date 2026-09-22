import unittest

from llama.llm_fields.location.waterBody import WaterBody


class TestWaterBody(unittest.TestCase):
    def test_water_body_01(self) -> None:
        """Value present in the text is kept (case-insensitive)."""
        assert (
            WaterBody("along the Fraser River", "Fraser River").waterBody
            == "Fraser River"
        )

    def test_water_body_02(self) -> None:
        """Value not present in the text is a hallucination and becomes empty."""
        assert WaterBody("on dry land", "Fraser River").waterBody == ""

    def test_water_body_03(self) -> None:
        """Empty text: everything is a hallucination."""
        assert WaterBody("", "Fraser River").waterBody == ""
