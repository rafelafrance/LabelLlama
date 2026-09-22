import unittest

from llama.line_align.align import GAP_CHAR
from llama.line_align.label_builder import find_consensus


class TestLabelBuilder(unittest.TestCase):
    def test_find_consensus_01(self) -> None:
        """With no copies the consensus is empty."""
        self.assertEqual(find_consensus([]), "")

    def test_find_consensus_02(self) -> None:
        """Short copies are padded before they vote."""
        self.assertEqual(find_consensus(["abc", "ab"]), "abc")

    def test_find_consensus_03(self) -> None:
        """A gap in every copy is dropped from the consensus."""
        self.assertEqual(
            find_consensus([GAP_CHAR * 2 + "ab", GAP_CHAR * 2 + "ac"]),
            "ab",
        )

    def test_find_consensus_04(self) -> None:
        """A gap can win a tie, dropping its column."""
        self.assertEqual(
            find_consensus(["ab", GAP_CHAR + "c", GAP_CHAR + "d"]),
            "b",
        )

    def test_find_consensus_05(self) -> None:
        """Gaps and disagreeing copies still give the majority line."""
        aligned = [
            (
                GAP_CHAR * 4
                + "MOJAVE DESERT, PROVIDENCE MTS.: canyon "
                + GAP_CHAR
                + "above"
            ),
            (
                "E."
                + GAP_CHAR
                + " MOJAVE DESERT, PROVIDENCE MTS.: canyon "
                + GAP_CHAR
                + "above"
            ),
            (
                "E"
                + GAP_CHAR * 2
                + " MOJAVE DESERT"
                + GAP_CHAR
                + " PROVTDENCE MTS.# canyon "
                + GAP_CHAR
                + "above"
            ),
            ("Be 'MOJAVE DESERT, PROVIDENCE " + GAP_CHAR * 6 + 'canyon "above'),
        ]
        self.assertEqual(
            find_consensus(aligned),
            "E MOJAVE DESERT, PROVIDENCE MTS.: canyon above",
        )

    def test_find_consensus_06(self) -> None:
        """Ties are broken by the character key, so "b" beats "c"."""
        self.assertEqual(find_consensus(["ab", "ac"]), "ab")

    def test_find_consensus_07(self) -> None:
        """PO weights order punctuation, so "." beats ","."""
        self.assertEqual(find_consensus(["a,", "a."]), "a.")
