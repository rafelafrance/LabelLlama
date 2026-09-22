import unittest

from llama.llm_fields.plants.plantHeight import PlantHeight


class TestPlantHeight(unittest.TestCase):
    def test_plant_height_01(self) -> None:
        """A plain value passes through unchanged (no hallucination check here)."""
        assert PlantHeight("any text", "10 m").plantHeight == "10 m"

    def test_plant_height_02(self) -> None:
        """Non-string values are converted to strings."""
        assert PlantHeight("", 123).plantHeight == "123"
        assert PlantHeight("", 1.5).plantHeight == "1.5"

    def test_plant_height_03(self) -> None:
        """None and nan become empty."""
        assert PlantHeight("", None).plantHeight == ""
        assert PlantHeight("", float("nan")).plantHeight == ""

    def test_plant_height_04(self) -> None:
        """Empty-value notations and surrounding whitespace are handled."""
        assert PlantHeight("", "none").plantHeight == ""
        assert PlantHeight("", " 2 m ").plantHeight == "2 m"
