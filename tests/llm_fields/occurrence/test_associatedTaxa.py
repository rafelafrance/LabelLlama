import unittest

from llama.llm_fields.occurrence.associatedTaxa import AssociatedTaxa


class TestAssociatedTaxa(unittest.TestCase):
    def test_associated_taxa_01(self) -> None:
        """A plain value passes through unchanged."""
        assert AssociatedTaxa("", "Aphis gossypii").associatedTaxa == "Aphis gossypii"

    def test_associated_taxa_02(self) -> None:
        """Markdown emphasis markers are removed."""
        assert AssociatedTaxa("", "*Aphis gossypii*").associatedTaxa == "Aphis gossypii"
        assert AssociatedTaxa("", "_Aphis gossypii_").associatedTaxa == "Aphis gossypii"

    def test_associated_taxa_03(self) -> None:
        """Trailing punctuation is removed."""
        assert AssociatedTaxa("", "Aphis gossypii,").associatedTaxa == "Aphis gossypii"
        assert AssociatedTaxa("", "Aphis gossypii .").associatedTaxa == "Aphis gossypii"

    def test_associated_taxa_04(self) -> None:
        """Whitespace is normalized to single spaces."""
        assert (
            AssociatedTaxa("", "  multiple   spaces  ").associatedTaxa
            == "multiple spaces"
        )

    def test_associated_taxa_05(self) -> None:
        """Multiple taxa separated by punctuation are kept together."""
        assert (
            AssociatedTaxa("", "Taxon A; Taxon B").associatedTaxa == "Taxon A; Taxon B"
        )

    def test_associated_taxa_06(self) -> None:
        """Empty input and empty-value notations stay empty."""
        assert AssociatedTaxa("", "").associatedTaxa == ""
        assert AssociatedTaxa("", "none").associatedTaxa == ""
