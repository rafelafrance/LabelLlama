import unittest

from llama.llm_fields.occurrence.occurrenceRemarks import OccurrenceRemarks


class TestOccurrenceRemarks(unittest.TestCase):
    def test_occurrence_remarks_01(self) -> None:
        """A plain remark passes through unchanged."""
        assert (
            OccurrenceRemarks("", "Found near river").occurrenceRemarks
            == "Found near river"
        )

    def test_occurrence_remarks_02(self) -> None:
        """Empty input and empty-value notations stay empty."""
        assert OccurrenceRemarks("", "").occurrenceRemarks == ""
        assert OccurrenceRemarks("", "none").occurrenceRemarks == ""

    def test_occurrence_remarks_03(self) -> None:
        """Whitespace is normalized to single spaces."""
        assert (
            OccurrenceRemarks("", "  spaced   out  ").occurrenceRemarks == "spaced out"
        )

    def test_occurrence_remarks_04(self) -> None:
        """A value that is only ID numbers is cleared."""
        assert OccurrenceRemarks("", "123").occurrenceRemarks == ""
        assert OccurrenceRemarks("", "123 456").occurrenceRemarks == ""

    def test_occurrence_remarks_05(self) -> None:
        """The "#" and "Nº" ID labels are stripped before the ID-number check."""
        assert OccurrenceRemarks("", "#123").occurrenceRemarks == ""
        assert OccurrenceRemarks("", "Nº 123").occurrenceRemarks == ""

    def test_occurrence_remarks_06(self) -> None:
        """A number mixed with real remark text is kept."""
        assert (
            OccurrenceRemarks("", "Found near river 123").occurrenceRemarks
            == "Found near river 123"
        )

    def test_score_07(self) -> None:
        """The scoring method is FPR and a substring scores 1.0."""
        assert OccurrenceRemarks.scoring_method == "FPR"
        assert OccurrenceRemarks.score("found near", "found near river", {}) == 1.0

    def test_score_08(self) -> None:
        """Fuzzy partial ratio: expected contained in actual scores full."""
        assert (
            OccurrenceRemarks.score("found near", "a specimen found near river", {})
            == 1.0
        )

    def test_score_09(self) -> None:
        """Dissimilar values score below 1.0."""
        score = OccurrenceRemarks.score("mangrove", "desert", {})
        assert 0.0 <= score < 1.0
