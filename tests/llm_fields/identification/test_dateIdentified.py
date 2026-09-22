import unittest

from llama.llm_fields.identification.dateIdentified import DateIdentified


class TestDateIdentified(unittest.TestCase):
    def test_date_identified_01(self) -> None:
        """Date values are not normalized."""
        assert DateIdentified("", "25 May 2024").dateIdentified == "25 May 2024"

    def test_date_identified_02(self) -> None:
        """Leading "Date:" label is removed."""
        assert DateIdentified("", "Date: 25 May 2024").dateIdentified == "25 May 2024"

    def test_date_identified_03(self) -> None:
        """Label removal is case-insensitive and separator-agnostic."""
        assert DateIdentified("", "date 25 May 2024").dateIdentified == "25 May 2024"
        assert DateIdentified("", "DATE, 25 May 2024").dateIdentified == "25 May 2024"

    def test_date_identified_04(self) -> None:
        """Empty inputs stay empty."""
        assert DateIdentified("", "").dateIdentified == ""
        assert DateIdentified("", "not present").dateIdentified == ""
        assert DateIdentified("", "Date:").dateIdentified == ""

    def test_date_identified_05(self) -> None:
        """A date range is left exactly as it was written."""
        assert (
            DateIdentified("", "25 May 2024|30 May 2024").dateIdentified
            == "25 May 2024|30 May 2024"
        )
