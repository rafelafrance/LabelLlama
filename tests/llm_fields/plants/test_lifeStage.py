import unittest

from llama.llm_fields.plants.lifeStage import LifeStage


class TestLifeStage(unittest.TestCase):
    def test_life_stage_01(self) -> None:
        """A value present in the text is kept."""
        assert (
            LifeStage("the specimen is in flowering", "flowering").lifeStage
            == "flowering"
        )

    def test_life_stage_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert LifeStage("currently FRUITING", "fruiting").lifeStage == "fruiting"

    def test_life_stage_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert LifeStage("the specimen is in flowering", "dormant").lifeStage == ""

    def test_life_stage_04(self) -> None:
        """An empty value stays empty."""
        assert LifeStage("some text", "").lifeStage == ""
