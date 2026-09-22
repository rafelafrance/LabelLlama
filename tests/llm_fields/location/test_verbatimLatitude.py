import unittest

from llama.llm_fields.location.verbatimLatitude import VerbatimLatitude


class TestVerbatimLatitude(unittest.TestCase):
    def test_verbatim_latitude_01(self) -> None:
        """DMS-formatted values are kept verbatim."""
        assert VerbatimLatitude("", "45\u00b030'N").verbatimLatitude == "45\u00b030'N"

    def test_verbatim_latitude_02(self) -> None:
        """Decimal values with direction letters are kept verbatim."""
        assert VerbatimLatitude("", "45.5 N").verbatimLatitude == "45.5 N"

    def test_verbatim_latitude_03(self) -> None:
        """Empty inputs and empty-value notations stay empty."""
        assert VerbatimLatitude("", "").verbatimLatitude == ""
        assert VerbatimLatitude("", "none").verbatimLatitude == ""

    def test_verbatim_latitude_04(self) -> None:
        """Non-string values are converted to strings."""
        assert VerbatimLatitude("", 45).verbatimLatitude == "45"
        assert VerbatimLatitude("", None).verbatimLatitude == ""
