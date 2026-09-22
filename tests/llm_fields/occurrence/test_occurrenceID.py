import unittest

from llama.llm_fields.occurrence.occurrenceID import OccurrenceID


class TestOccurrenceID(unittest.TestCase):
    def test_occurrence_id_01(self) -> None:
        """A plain value passes through unchanged."""
        assert OccurrenceID("", "ABC-123").occurrenceID == "ABC-123"

    def test_occurrence_id_02(self) -> None:
        """The "#" and "Nº" labels are stripped."""
        assert OccurrenceID("", "#123").occurrenceID == "123"
        assert OccurrenceID("", "Nº 123").occurrenceID == "123"

    def test_occurrence_id_03(self) -> None:
        """The "no"/"number"/"num" label is removed, case-insensitively."""
        assert OccurrenceID("", "no 123").occurrenceID == "123"
        assert OccurrenceID("", "No: 123").occurrenceID == "123"
        assert OccurrenceID("", "No. 55").occurrenceID == "55"
        assert OccurrenceID("", "number 456").occurrenceID == "456"
        assert OccurrenceID("", "NUMBER 9").occurrenceID == "9"
        assert OccurrenceID("", "num, 789").occurrenceID == "789"

    def test_occurrence_id_04(self) -> None:
        """A value that is only the label becomes empty."""
        assert OccurrenceID("", "number").occurrenceID == ""

    def test_occurrence_id_05(self) -> None:
        """Empty input and empty-value notations stay empty."""
        assert OccurrenceID("", "").occurrenceID == ""
        assert OccurrenceID("", "none").occurrenceID == ""
