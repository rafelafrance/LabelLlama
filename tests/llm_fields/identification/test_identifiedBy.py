import unittest

from llama.llm_fields.identification.identifiedBy import IdentifiedBy


class TestIdentifiedBy(unittest.TestCase):
    def test_identified_by_01(self) -> None:
        """Name passes through unchanged."""
        assert IdentifiedBy("", "John Doe").identifiedBy == "John Doe"

    def test_identified_by_02(self) -> None:
        """Punctuation and titles within the name are preserved."""
        assert IdentifiedBy("", "John Doe, PhD").identifiedBy == "John Doe, PhD"

    def test_identified_by_03(self) -> None:
        """Empty-value notations become an empty string."""
        assert IdentifiedBy("", "").identifiedBy == ""
        assert IdentifiedBy("", "none").identifiedBy == ""
        assert IdentifiedBy("", "not present").identifiedBy == ""

    def test_identified_by_04(self) -> None:
        """Markdown and list wrappers are cleaned."""
        assert IdentifiedBy("", "**John Doe**").identifiedBy == "John Doe"
        assert IdentifiedBy("", ["John", "Doe"]).identifiedBy == "John Doe"
