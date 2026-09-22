import unittest

from llama.calc_fields.plants.fruitPresent import FruitPresent


class TestFruitPresent(unittest.TestCase):
    def test_fruit_present_01(self) -> None:
        """A fruit colour means fruit is present."""
        rec = {"fruitColor": "red"}
        assert FruitPresent(rec, "").fruitPresent is True

    def test_fruit_present_02(self) -> None:
        """Fruit facts alone mean fruit is present."""
        rec = {"fruitFacts": "drupe, ripens in fall"}
        assert FruitPresent(rec, "").fruitPresent is True

    def test_fruit_present_03(self) -> None:
        """A record with no fruit evidence leaves it empty."""
        rec = {}
        assert FruitPresent(rec, "").fruitPresent == ""

    def test_fruit_present_04(self) -> None:
        """No record at all leaves the field empty."""
        assert FruitPresent(None, "").fruitPresent == ""

    def test_fruit_present_05(self) -> None:
        """Empty fruit fields are no evidence."""
        rec = {"fruitColor": "", "fruitFacts": ""}
        assert FruitPresent(rec, "").fruitPresent == ""

    def test_fruit_present_06(self) -> None:
        """An already-affirmative value is left untouched."""
        rec = {}
        assert FruitPresent(rec, True).fruitPresent is True  # noqa: FBT003

    def test_fruit_present_07(self) -> None:
        """Evidence (a fruit color) overrides an explicit False."""
        rec = {"fruitColor": "yellow"}
        assert FruitPresent(rec, False).fruitPresent is True  # noqa: FBT003


if __name__ == "__main__":
    unittest.main()
