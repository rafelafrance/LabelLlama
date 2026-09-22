import unittest

from llama.llm_fields.record_level.collectionCode import CollectionCode


class TestCollectionCode(unittest.TestCase):
    def test_collection_code_01(self) -> None:
        """A plain collection code passes through unchanged."""
        assert CollectionCode("", "CAS").collectionCode == "CAS"

    def test_collection_code_02(self) -> None:
        """Surrounding whitespace is stripped."""
        assert CollectionCode("", "  NY  ").collectionCode == "NY"

    def test_collection_code_03(self) -> None:
        """Empty input and empty-value notations stay empty."""
        assert CollectionCode("", "").collectionCode == ""
        assert CollectionCode("", "none").collectionCode == ""
        assert CollectionCode("", "not present").collectionCode == ""

    def test_collection_code_04(self) -> None:
        """Non-string values are converted to strings."""
        assert CollectionCode("", None).collectionCode == ""
        assert CollectionCode("", 123).collectionCode == "123"
        assert CollectionCode("", float("nan")).collectionCode == ""

    def test_collection_code_05(self) -> None:
        """Markdown emphasis is cleaned."""
        assert CollectionCode("", "**CAS**").collectionCode == "CAS"
