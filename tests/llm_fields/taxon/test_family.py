import unittest

from llama.llm_fields.taxon.family import Family


class TestFamily(unittest.TestCase):
    def test_family_01(self) -> None:
        """Family names are title-cased."""
        assert Family("", "rosaceae").family == "Rosaceae"
        assert Family("", "ROSACEAE").family == "Rosaceae"

    def test_family_02(self) -> None:
        """Empty input stays empty."""
        assert Family("", "").family == ""

    def test_family_03(self) -> None:
        """Non-string values are converted to strings."""
        assert Family("", None).family == ""
        assert Family("", 123).family == "123"

    def test_score_04(self) -> None:
        """Scoring is custom ("CUST"), and identical values score 1.0."""
        assert Family.scoring_method == "CUST"
        assert (
            Family.score("Rosaceae", "Rosaceae", {"scientificName": "Rosa gallica"})
            == 1.0
        )

    def test_score_05(self) -> None:
        """An empty expectation matching the genus' family scores 1.0."""
        assert Family.score("", "Rosaceae", {"scientificName": "Rosa gallica"}) == 1.0

    def test_score_06(self) -> None:
        """An empty expectation against the genus scores zero."""
        assert Family.score("", "Asteraceae", {"scientificName": "Rosa gallica"}) == 0.0

    def test_score_07(self) -> None:
        """A genus not in the lookup table cannot earn the free 1.0."""
        assert Family.score("", "Rosaceae", {"scientificName": "Canis latrans"}) == 0.0

    def test_score_08(self) -> None:
        """With a non-empty expectation, dissimilar values score below 1.0."""
        assert (
            0.0
            <= Family.score(
                "Asteraceae", "Rosaceae", {"scientificName": "Rosa gallica"}
            )
            < 1.0
        )

    def test_score_09(self) -> None:
        """A missing scientificName falls back to edit distance (0.0 vs non-empty)."""
        assert Family.score("", "Rosaceae", {}) == 0.0
