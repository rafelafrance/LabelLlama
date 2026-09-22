import unittest

from llama.calc_fields.event.eventDate import EventDate


class TestEventDate(unittest.TestCase):
    """Verbatim event dates become ISO dates, alone or as a range."""

    def test_event_date_01(self) -> None:
        """A complete ISO date is copied through unchanged."""
        record = {"verbatimEventDate": "1990-05-01"}
        assert EventDate(record, "").eventDate == "1990-05-01"

    def test_event_date_02(self) -> None:
        """A month name and year are reduced to a year-month date."""
        record = {"verbatimEventDate": "May 1990"}
        assert EventDate(record, "").eventDate == "1990-05"

    def test_event_date_03(self) -> None:
        """A pipe separated range of full dates is joined with ' to '."""
        record = {"verbatimEventDate": "1990-05-01|1990-05-03"}
        assert EventDate(record, "").eventDate == "1990-05-01 to 1990-05-03"

    def test_event_date_04(self) -> None:
        """A pipe separated range of months is joined with ' to '."""
        record = {"verbatimEventDate": "May 1990 | June 1990"}
        assert EventDate(record, "").eventDate == "1990-05 to 1990-06"

    def test_event_date_05(self) -> None:
        """An empty verbatim date gives an empty event date."""
        record = {"verbatimEventDate": ""}
        assert EventDate(record, "").eventDate == ""

    def test_event_date_06(self) -> None:
        """A record without the verbatim date key gives an empty event date."""
        assert EventDate({}, "").eventDate == ""

    def test_event_date_07(self) -> None:
        """A None verbatim date gives an empty event date."""
        record = {"verbatimEventDate": None}
        assert EventDate(record, "").eventDate == ""

    def test_event_date_08(self) -> None:
        """A NaN verbatim date, read from an empty CSV cell, gives blank."""
        record = {"verbatimEventDate": float("nan")}
        assert EventDate(record, "").eventDate == ""

    def test_event_date_09(self) -> None:
        """A range keeps a valid first date and drops an unparseable second."""
        record = {"verbatimEventDate": "1990-05-01|not a date"}
        assert EventDate(record, "").eventDate == "1990-05-01"

    def test_event_date_10(self) -> None:
        """A range keeps a valid last date and drops an unparseable first."""
        record = {"verbatimEventDate": "n/a|1990-05-03"}
        assert EventDate(record, "").eventDate == "1990-05-03"

    def test_event_date_11(self) -> None:
        """A range with no parseable date at all gives an empty event date."""
        record = {"verbatimEventDate": "n/a|also n/a"}
        assert EventDate(record, "").eventDate == ""


if __name__ == "__main__":
    unittest.main()
