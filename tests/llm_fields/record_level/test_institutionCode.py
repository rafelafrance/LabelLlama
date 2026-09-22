import unittest

from llama.llm_fields.record_level.institutionCode import InstitutionCode


class TestInstitutionCode(unittest.TestCase):
    def test_institution_code_01(self) -> None:
        """A plain institution code passes through unchanged."""
        assert InstitutionCode("", "USNM").institutionCode == "USNM"

    def test_institution_code_02(self) -> None:
        """Surrounding whitespace is stripped."""
        assert InstitutionCode("", "  MCZ  ").institutionCode == "MCZ"

    def test_institution_code_03(self) -> None:
        """Empty input and empty-value notations stay empty."""
        assert InstitutionCode("", "").institutionCode == ""
        assert InstitutionCode("", "none").institutionCode == ""
        assert InstitutionCode("", "not present").institutionCode == ""

    def test_institution_code_04(self) -> None:
        """Non-string values are converted to strings."""
        assert InstitutionCode("", None).institutionCode == ""
        assert InstitutionCode("", 42).institutionCode == "42"
        assert InstitutionCode("", float("nan")).institutionCode == ""

    def test_institution_code_05(self) -> None:
        """Markdown emphasis is cleaned."""
        assert InstitutionCode("", "**MCZ**").institutionCode == "MCZ"
