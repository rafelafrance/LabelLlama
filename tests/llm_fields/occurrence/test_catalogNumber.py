import unittest

from llama.llm_fields.occurrence.catalogNumber import CatalogNumber


class TestCatalogNumber(unittest.TestCase):
    def test_catalog_number_01(self) -> None:
        """A plain value passes through unchanged."""
        assert CatalogNumber("", "ABC-123").catalogNumber == "ABC-123"

    def test_catalog_number_02(self) -> None:
        """Surrounding whitespace is stripped."""
        assert CatalogNumber("", "  X1  ").catalogNumber == "X1"

    def test_catalog_number_03(self) -> None:
        """Empty input and empty-value notations stay empty."""
        assert CatalogNumber("", "").catalogNumber == ""
        assert CatalogNumber("", "none").catalogNumber == ""

    def test_catalog_number_04(self) -> None:
        """Non-string values are converted to strings."""
        assert CatalogNumber("", None).catalogNumber == ""
        assert CatalogNumber("", 123).catalogNumber == "123"
        assert CatalogNumber("", float("nan")).catalogNumber == ""
