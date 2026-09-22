import unittest

from llama.llm_fields.plants.plantSizes import PlantSizes


class TestPlantSizes(unittest.TestCase):
    def test_plant_sizes_01(self) -> None:
        """A single string passes through unchanged."""
        assert PlantSizes("", "1 cm").plantSizes == "1 cm"

    def test_plant_sizes_02(self) -> None:
        """A single-item list reduces to that item."""
        assert PlantSizes("", ["1 cm"]).plantSizes == "1 cm"

    def test_plant_sizes_03(self) -> None:
        """Multiple items are reduced to the list's string form."""
        assert PlantSizes("", ["1 cm", "2 cm"]).plantSizes == "1 cm, 2 cm"

    def test_plant_sizes_04(self) -> None:
        """Empty input and the default (no value) become an empty string."""
        assert PlantSizes("", []).plantSizes == ""
        assert PlantSizes("").plantSizes == ""

    def test_plant_sizes_05(self) -> None:
        """Non-string values are converted to strings."""
        assert PlantSizes("", 5).plantSizes == "5"
