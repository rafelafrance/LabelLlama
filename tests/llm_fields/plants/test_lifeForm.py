import unittest

from llama.llm_fields.plants.lifeForm import LifeForm


class TestLifeForm(unittest.TestCase):
    def test_life_form_01(self) -> None:
        """A value present in the text is kept."""
        assert LifeForm("a tall forb in the meadow", "forb").lifeForm == "forb"

    def test_life_form_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert LifeForm("a GRASS species", "grass").lifeForm == "grass"

    def test_life_form_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert LifeForm("a tall forb in the meadow", "tree").lifeForm == ""

    def test_life_form_04(self) -> None:
        """An empty value stays empty."""
        assert LifeForm("some text", "").lifeForm == ""
