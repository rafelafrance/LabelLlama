import unittest

from llama.llm_fields.occurrence.recordNumber import RecordNumber


class TestRecordNumber(unittest.TestCase):
    def test_record_number_01(self) -> None:
        """A plain value passes through unchanged."""
        assert RecordNumber("", "12345").recordNumber == "12345"

    def test_record_number_02(self) -> None:
        """The "#" and "Nº" labels are stripped."""
        assert RecordNumber("", "#123").recordNumber == "123"
        assert RecordNumber("", "Nº 123").recordNumber == "123"

    def test_record_number_03(self) -> None:
        """The "no"/"number"/"num" label is removed, case-insensitively."""
        assert RecordNumber("", "no 123").recordNumber == "123"
        assert RecordNumber("", "No: 123").recordNumber == "123"
        assert RecordNumber("", "No. 55").recordNumber == "55"
        assert RecordNumber("", "number 456").recordNumber == "456"
        assert RecordNumber("", "NUM 55").recordNumber == "55"
        assert RecordNumber("", "num, 789").recordNumber == "789"

    def test_record_number_04(self) -> None:
        """A value that is only the label becomes empty."""
        assert RecordNumber("", "number").recordNumber == ""

    def test_record_number_05(self) -> None:
        """Empty input and empty-value notations stay empty."""
        assert RecordNumber("", "").recordNumber == ""
        assert RecordNumber("", "none").recordNumber == ""
