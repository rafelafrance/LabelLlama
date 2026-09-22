import unittest

from llama.llm_fields.location.locality import Locality


class TestLocality(unittest.TestCase):
    def test_locality_01(self) -> None:
        """A plain value passes through unchanged."""
        assert (
            Locality("", "Pond near canal off CR 800").locality
            == "Pond near canal off CR 800"
        )

    def test_locality_02(self) -> None:
        """Empty input stays empty."""
        assert Locality("", "").locality == ""

    def test_locality_03(self) -> None:
        """Empty-value notations become an empty string."""
        assert Locality("", "none").locality == ""
        assert Locality("", "not present").locality == ""

    def test_locality_04(self) -> None:
        """Non-string values are converted to strings."""
        assert Locality("", float("nan")).locality == ""
        assert Locality("", 123).locality == "123"
        assert Locality("", ["Pond", "near", "canal"]).locality == "Pond near canal"

    def test_score_05(self) -> None:
        """The scoring method is FPR and equal values score 1.0."""
        assert Locality.scoring_method == "FPR"
        assert Locality.score("forest", "forest", {}) == 1.0

    def test_score_06(self) -> None:
        """Fuzzy partial ratio: expected contained in actual scores full."""
        assert Locality.score("forest", "a forest area", {}) == 1.0

    def test_score_07(self) -> None:
        """Dissimilar values score below 1.0."""
        score = Locality.score("mangrove", "desert", {})
        assert 0.0 <= score < 1.0
