import unittest

from llama.llm_fields.plants.lifeCycle import LifeCycle


class TestLifeCycle(unittest.TestCase):
    def test_life_cycle_01(self) -> None:
        """A value present in the text is kept."""
        assert LifeCycle("a perennial plant", "perennial").lifeCycle == "perennial"

    def test_life_cycle_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert LifeCycle("a BIENNIAL species", "biennial").lifeCycle == "biennial"

    def test_life_cycle_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert LifeCycle("a perennial plant", "annual").lifeCycle == ""

    def test_life_cycle_04(self) -> None:
        """An empty value stays empty."""
        assert LifeCycle("some text", "").lifeCycle == ""
