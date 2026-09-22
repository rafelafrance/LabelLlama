import unittest

from llama.llm_fields.event.habitat import Habitat


class TestHabitat(unittest.TestCase):
    def test_habitat_01(self) -> None:
        """Plain value passes through unchanged."""
        assert Habitat("", "forest").habitat == "forest"

    def test_habitat_02(self) -> None:
        """Leading "Habitat:" label is removed."""
        assert Habitat("", "Habitat: forest").habitat == "forest"

    def test_habitat_03(self) -> None:
        """Label removal is case-insensitive."""
        assert Habitat("", "habitat Forest").habitat == "Forest"
        assert Habitat("", "HABITAT: Forest").habitat == "Forest"

    def test_habitat_04(self) -> None:
        """Label removal handles various separators."""
        assert Habitat("", "habitat, forest").habitat == "forest"
        assert Habitat("", "habitat; forest").habitat == "forest"
        assert Habitat("", "habitat. forest").habitat == "forest"
        assert Habitat("", "habitat  forest").habitat == "forest"

    def test_habitat_05(self) -> None:
        """A value that is only the label becomes empty."""
        assert Habitat("", "Habitat:").habitat == ""

    def test_habitat_06(self) -> None:
        """Empty-value notations become an empty string."""
        assert Habitat("", "none").habitat == ""
        assert Habitat("", "not present").habitat == ""
        assert Habitat("", float("nan")).habitat == ""

    def test_score_07(self) -> None:
        """The scoring method is FPR and equal values score 1.0."""
        assert Habitat.scoring_method == "FPR"
        assert Habitat.score("forest", "forest", {}) == 1.0

    def test_score_08(self) -> None:
        """Fuzzy partial ratio: expected contained in actual scores full."""
        assert Habitat.score("forest", "a forest area", {}) == 1.0

    def test_score_09(self) -> None:
        """Dissimilar values score below 1.0."""
        score = Habitat.score("mangrove", "desert", {})
        assert 0.0 <= score < 1.0

    def test_habitat_10(self) -> None:
        """Plural labels are also removed."""
        assert Habitat("", "Habitats: forest").habitat == "forest"
