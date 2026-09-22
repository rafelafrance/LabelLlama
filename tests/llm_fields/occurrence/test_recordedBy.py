import unittest

from llama.llm_fields.occurrence.recordedBy import RecordedBy


class TestRecordedBy(unittest.TestCase):
    def test_recorded_by_01(self) -> None:
        """A plain name passes through unchanged."""
        assert RecordedBy("", "John Doe").recordedBy == "John Doe"

    def test_recorded_by_02(self) -> None:
        """Empty input and empty-value notations stay empty."""
        assert RecordedBy("", "").recordedBy == ""
        assert RecordedBy("", "none").recordedBy == ""

    def test_recorded_by_03(self) -> None:
        """The lowercase collector label is removed."""
        assert RecordedBy("", "coll: John Doe").recordedBy == "John Doe"
        assert RecordedBy("", "coll. John Doe").recordedBy == "John Doe"
        assert RecordedBy("", "coll John Doe").recordedBy == "John Doe"
        assert RecordedBy("", "col John Doe").recordedBy == "John Doe"
        assert RecordedBy("", "collector, Jane Roe").recordedBy == "Jane Roe"

    def test_recorded_by_04(self) -> None:
        """The capitalized Collector label is removed."""
        assert RecordedBy("", "Collector: John Doe").recordedBy == "John Doe"

    def test_recorded_by_05(self) -> None:
        """An all-caps COLLECTOR label is removed."""
        assert RecordedBy("", "COLLECTOR: John Doe").recordedBy == "John Doe"

    def test_recorded_by_06(self) -> None:
        """A capitalized Coll label is removed."""
        assert RecordedBy("", "Coll: John Doe").recordedBy == "John Doe"

    def test_recorded_by_07(self) -> None:
        """A collector label without a colon is removed."""
        assert RecordedBy("", "Collector John Doe").recordedBy == "John Doe"
