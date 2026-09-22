import unittest

from llama.llm_fields.insects.lifeStage import LifeStage


class TestLifeStage(unittest.TestCase):
    def test_life_stage_01(self) -> None:
        """Value present in the text is kept."""
        assert LifeStage("A larva was collected.", "larva").lifeStage == "larva"

    def test_life_stage_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert LifeStage("a larva was collected", "Larva").lifeStage == "Larva"

    def test_life_stage_03(self) -> None:
        """Multi-word values present in the text are kept."""
        assert (
            LifeStage("Specimen is a teneral adult.", "teneral adult").lifeStage
            == "teneral adult"
        )

    def test_life_stage_04(self) -> None:
        """Value not present in the text is a hallucination and becomes empty."""
        assert LifeStage("adult beetle", "nymph").lifeStage == ""

    def test_life_stage_05(self) -> None:
        """Empty text: means everything is a hallucination."""
        assert LifeStage("", "exuvia").lifeStage == ""

    def test_life_stage_06(self) -> None:
        """Empty inputs and empty-value notations stay empty."""
        assert LifeStage("some text", "").lifeStage == ""
        assert LifeStage("some text", "none").lifeStage == ""

    def test_life_stage_07(self) -> None:
        """Regex-special characters in the value are matched literally."""
        assert (
            LifeStage("det: adult (male)", "adult (male)").lifeStage == "adult (male)"
        )
        assert LifeStage("det: adult (male", "adult (male)").lifeStage == ""
