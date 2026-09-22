import unittest

from llama.llm_fields.location.verbatimLongitude import VerbatimLongitude


class TestVerbatimLongitude(unittest.TestCase):
    def test_verbatim_longitude_01(self) -> None:
        """DMS-formatted values are kept verbatim."""
        assert (
            VerbatimLongitude("", "122\u00b015'W").verbatimLongitude == "122\u00b015'W"
        )

    def test_verbatim_longitude_02(self) -> None:
        """Decimal values with direction letters are kept verbatim."""
        assert VerbatimLongitude("", "W 122.5").verbatimLongitude == "W 122.5"

    def test_verbatim_longitude_03(self) -> None:
        """Empty inputs and empty-value notations stay empty."""
        assert VerbatimLongitude("", "").verbatimLongitude == ""
        assert VerbatimLongitude("", "none").verbatimLongitude == ""
