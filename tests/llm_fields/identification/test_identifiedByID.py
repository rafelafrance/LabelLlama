import unittest

from llama.llm_fields.identification.identifiedByID import IdentifiedByID


class TestIdentifiedByID(unittest.TestCase):
    def test_identified_by_id_01(self) -> None:
        """Plain ID passes through unchanged."""
        assert IdentifiedByID("", "12345").identifiedByID == "12345"
        assert IdentifiedByID("", "GBIF:12345").identifiedByID == "GBIF:12345"

    def test_identified_by_id_02(self) -> None:
        """A 'No' or 'Number' label in front of the digits is removed."""
        assert IdentifiedByID("", "No. 12345").identifiedByID == "12345"
        assert IdentifiedByID("", "no 12345").identifiedByID == "12345"
        assert IdentifiedByID("", "Number: 12345").identifiedByID == "12345"
        assert IdentifiedByID("", "num 12345").identifiedByID == "12345"

    def test_identified_by_id_03(self) -> None:
        """Prefix markers are removed."""
        assert IdentifiedByID("", "#12345").identifiedByID == "12345"
        assert IdentifiedByID("", "Nº 12345").identifiedByID == "12345"

    def test_identified_by_id_04(self) -> None:
        """Empty inputs stay empty."""
        assert IdentifiedByID("", "").identifiedByID == ""
        assert IdentifiedByID("", "none").identifiedByID == ""

    def test_identified_by_id_05(self) -> None:
        """Lowercase ordinal without a space is removed."""
        assert IdentifiedByID("", "nº12345").identifiedByID == "12345"

    def test_identified_by_id_06(self) -> None:
        """Combined prefix markers and label+dot without space are removed."""
        assert IdentifiedByID("", "# Nº 12345").identifiedByID == "12345"
        assert IdentifiedByID("", "No.12345").identifiedByID == "12345"

    def test_identified_by_id_10(self) -> None:
        """Lowercase ordinal prefix is removed (case-insensitive)."""
        assert IdentifiedByID("", "nº 12345").identifiedByID == "12345"

    def test_identified_by_id_11(self) -> None:
        """
        Both a label and a following '#' are dropped.

        The '#' leaves a word boundary after the label, so the label still
        matches.
        """
        assert IdentifiedByID("", "No#12345").identifiedByID == "12345"
        assert IdentifiedByID("", "number#12345").identifiedByID == "12345"

    def test_identified_by_id_12(self) -> None:
        """Label glued to the digits is removed."""
        assert IdentifiedByID("", "no12345").identifiedByID == "12345"

    def test_identified_by_id_13(self) -> None:
        """The degree sign counts as an ordinal marker."""
        assert IdentifiedByID("", "N\u00b0 12345").identifiedByID == "12345"

    def test_identified_by_id_14(self) -> None:
        """Words that only look like a label are left alone."""
        assert IdentifiedByID("", "non-12345").identifiedByID == "non-12345"
        assert IdentifiedByID("", "renumber 12345").identifiedByID == "renumber 12345"
