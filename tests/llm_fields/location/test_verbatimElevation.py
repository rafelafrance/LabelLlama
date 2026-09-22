import unittest

from llama.llm_fields.location.verbatimElevation import VerbatimElevation


class TestVerbatimElevation(unittest.TestCase):
    def test_verbatim_elevation_01(self) -> None:
        """The "elevation" label is removed."""
        assert VerbatimElevation("", "elevation 1200 m").verbatimElevation == "1200 m"

    def test_verbatim_elevation_02(self) -> None:
        """Label removal is case-insensitive and handles abbreviations."""
        assert VerbatimElevation("", "el. 1200 m").verbatimElevation == "1200 m"
        assert VerbatimElevation("", "ALT 1200 m").verbatimElevation == "1200 m"
        assert VerbatimElevation("", "altitude: 1200").verbatimElevation == "1200"

    def test_verbatim_elevation_03(self) -> None:
        """A value without a label is unchanged."""
        assert VerbatimElevation("", "1200 m").verbatimElevation == "1200 m"

    def test_verbatim_elevation_04(self) -> None:
        """Empty inputs and empty-value notations stay empty."""
        assert VerbatimElevation("", "").verbatimElevation == ""
        assert VerbatimElevation("", "none").verbatimElevation == ""

    def test_verbatim_elevation_10(self) -> None:
        """Keep words that look like labels."""
        assert (
            VerbatimElevation("", "1200 m near El Alto").verbatimElevation
            == "1200 m near El Alto"
        )
