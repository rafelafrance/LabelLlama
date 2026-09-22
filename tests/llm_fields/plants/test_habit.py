import unittest

from llama.llm_fields.plants.habit import Habit


class TestHabit(unittest.TestCase):
    def test_habit_01(self) -> None:
        """A value present in the text is kept."""
        assert Habit("The plant is a shrub.", "shrub").habit == "shrub"

    def test_habit_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert Habit("a tall shrub grows", "Shrub").habit == "Shrub"

    def test_habit_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert Habit("a tree here", "shrub").habit == ""

    def test_habit_04(self) -> None:
        """Empty text means everything is a hallucination."""
        assert Habit("", "shrub").habit == ""

    def test_habit_05(self) -> None:
        """An empty value stays empty."""
        assert Habit("some text", "").habit == ""

    def test_habit_06(self) -> None:
        """Regex-special characters in the value are matched literally."""
        assert Habit("det: shrub (dense)", "shrub (dense)").habit == "shrub (dense)"
        assert Habit("det: shrub dense", "shrub (dense)").habit == ""
