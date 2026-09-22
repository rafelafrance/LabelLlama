import unittest

from llama.line_align import char_sub_matrix
from llama.line_align.align import LineAlign


class TestAlign(unittest.TestCase):
    matrix = char_sub_matrix.get()

    def setUp(self) -> None:
        two_chars = {"aa": 0.0, "ab": -1.0, "bb": 0.0}
        self.line = LineAlign(two_chars, -1.0, -1.0)

    def test_align_01(self) -> None:
        """Identical lines need no gaps."""
        self.assertEqual(self.line.align(["aba", "aba"]), ["aba", "aba"])

    def test_align_02(self) -> None:
        """A middle deletion lines up with a gap in the shorter line."""
        self.assertEqual(self.line.align(["aba", "aa"]), ["aba", "a⋄a"])

    def test_align_03(self) -> None:
        """The gap fills the shorter line however it is ordered."""
        self.assertEqual(self.line.align(["aa", "aba"]), ["a⋄a", "aba"])

    def test_align_04(self) -> None:
        """A character missing at the end leaves the gap last."""
        self.assertEqual(self.line.align(["aab", "aa"]), ["aab", "aa⋄"])

    def test_align_05(self) -> None:
        """A character missing at the front leaves the gap first."""
        self.assertEqual(self.line.align(["baa", "aa"]), ["baa", "⋄aa"])

    def test_align_06(self) -> None:
        """A front gap fills the shorter line given first."""
        self.assertEqual(self.line.align(["aa", "baa"]), ["⋄aa", "baa"])

    def test_align_07(self) -> None:
        """An end gap fills the shorter line given first."""
        self.assertEqual(self.line.align(["aa", "aab"]), ["aa⋄", "aab"])

    def test_align_08(self) -> None:
        """Equal length lines align without any gaps."""
        self.assertEqual(self.line.align(["aab", "baa"]), ["aab", "baa"])

    def test_align_09(self) -> None:
        """A single line is returned unchanged."""
        self.assertEqual(self.line.align(["aab"]), ["aab"])

    def test_align_10(self) -> None:
        """Aligning no lines gives no lines."""
        self.assertEqual(self.line.align([]), [])

    def test_align_11(self) -> None:
        """Progressive alignment of three lines needs no gaps."""
        self.assertEqual(self.line.align(["aab", "aaa", "aaa"]), ["aab", "aaa", "aaa"])

    def test_align_12(self) -> None:
        """Three equal length lines align column for column."""
        self.assertEqual(self.line.align(["aab", "abb", "aba"]), ["aab", "abb", "aba"])

    def test_align_13(self) -> None:
        """Real label copies are padded so their columns line up."""
        line = LineAlign(substitutions=self.matrix)
        results = line.align(
            [
                "MOJAVE DESERT, PROVIDENCE MTS.: canyon above",
                "E. MOJAVE DESERT , PROVIDENCE MTS . : canyon above",
                "E MOJAVE DESERT PROVTDENCE MTS. # canyon above",
                "Be ‘MOJAVE DESERT, PROVIDENCE canyon “above",
            ],
        )
        self.assertEqual(
            results,
            [
                "⋄⋄⋄⋄MOJAVE DESERT⋄, PROVIDENCE MTS⋄.⋄: canyon ⋄above",
                "E. ⋄MOJAVE DESERT , PROVIDENCE MTS . : canyon ⋄above",
                "E⋄ ⋄MOJAVE DESERT ⋄⋄PROVTDENCE MTS⋄. # canyon ⋄above",
                "Be ‘MOJAVE DESERT⋄, PROVIDENCE ⋄⋄⋄⋄⋄⋄⋄⋄canyon “above",
            ],
        )

    def test_align_14(self) -> None:
        """A much shorter copy aligns under the others as gaps."""
        line = LineAlign(self.matrix)
        results = line.align(
            [
                "Johns Island Sta tion on",
                " Johns Island Stati on on",
                "Johns Island Station on i",
                "Station or",
            ],
        )
        self.assertEqual(
            results,
            [
                "⋄Johns Island Sta ti⋄on on⋄⋄",
                " Johns Island Sta⋄ti on on⋄⋄",
                "⋄Johns Island Sta⋄ti⋄on on i",
                "⋄⋄⋄⋄⋄⋄⋄⋄⋄⋄⋄⋄⋄⋄Sta⋄ti⋄on or⋄⋄",
            ],
        )

    def test_align_15(self) -> None:
        """
        A mismatch costs less than the gaps that would avoid it.

        The default matrix scores "R" over "T" at -1.0, which is cheaper than
        the two extra gaps needed to bring "O" and "T" under each other.
        """
        line = LineAlign(self.matrix)
        results = line.align(
            [
                "North Carolina NORTH CAROLINA Guilford County",
                "North Carolina OT CAROLINA Guilford County",
            ],
        )
        self.assertEqual(
            results,
            [
                "North Carolina NORTH CAROLINA Guilford County",
                "North Carolina ⋄O⋄T⋄ CAROLINA Guilford County",
            ],
        )

    def test_align_16(self) -> None:
        """
        A gap block is kept contiguous instead of split across the row.

        With the default gap of -3.0 and skew of -0.5, "⋄⋄b" against "abb"
        scores -3.5 and the split "⋄b⋄" only -6.0.
        """
        line = LineAlign({"aa": 0.0, "ab": -1.0, "bb": 0.0})
        self.assertEqual(line.align(["b", "abb"]), ["⋄⋄b", "abb"])

    def test_align_17(self) -> None:
        """
        The single "a" is aligned under the last "a" of the longer line.

        One 3-gap block scores -4.0, better than a 2-gap block plus a trailing
        gap at -6.5.
        """
        line = LineAlign({"aa": 0.0, "ab": -1.0, "bb": 0.0})
        self.assertEqual(line.align(["a", "bbaa"]), ["⋄⋄⋄a", "bbaa"])

    def test_align_18(self) -> None:
        """
        "ba" is aligned under the trailing "ba", not an earlier one.

        One 3-gap block (-4.0) plus one mismatch (-1.0) beats splitting the
        gap (-6.5).
        """
        line = LineAlign({"aa": 0.0, "ab": -1.0, "bb": 0.0})
        self.assertEqual(line.align(["ba", "ababb"]), ["⋄⋄⋄ba", "ababb"])

    def test_align_19(self) -> None:
        """A contiguous gap block also wins when three lines are aligned."""
        line = LineAlign({"aa": 0.0, "ab": -1.0, "bb": 0.0})
        self.assertEqual(line.align(["b", "abb", "abb"]), ["⋄⋄b", "abb", "abb"])
