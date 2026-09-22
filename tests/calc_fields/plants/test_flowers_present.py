import unittest

from llama.calc_fields.plants.flowersPresent import FlowersPresent


class TestFlowersPresent(unittest.TestCase):
    def test_flowers_present_01(self) -> None:
        """A flower colour means flowers are present."""
        rec = {"flowerColor": "pink"}
        assert FlowersPresent(rec, "").flowersPresent is True

    def test_flowers_present_02(self) -> None:
        """Flower facts alone mean flowers are present."""
        rec = {"flowerFacts": "five petals"}
        assert FlowersPresent(rec, "").flowersPresent is True

    def test_flowers_present_03(self) -> None:
        """A record with no flower evidence leaves it empty."""
        rec = {}
        assert FlowersPresent(rec, "").flowersPresent == ""

    def test_flowers_present_04(self) -> None:
        """No record at all leaves the field empty."""
        assert FlowersPresent(None, "").flowersPresent == ""

    def test_flowers_present_05(self) -> None:
        """Empty flower fields are no evidence."""
        rec = {"flowerColor": "", "flowerFacts": ""}
        assert FlowersPresent(rec, "").flowersPresent == ""

    def test_flowers_present_06(self) -> None:
        """An already-affirmative value is left untouched."""
        rec = {}
        assert FlowersPresent(rec, True).flowersPresent is True  # noqa: FBT003

    def test_flowers_present_07(self) -> None:
        """Evidence (a flower color) overrides an explicit False."""
        rec = {"flowerColor": "red"}
        assert FlowersPresent(rec, False).flowersPresent is True  # noqa: FBT003


if __name__ == "__main__":
    unittest.main()
