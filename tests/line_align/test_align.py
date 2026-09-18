import unittest

from llama.line_align import char_sub_matrix
from llama.line_align.align import LineAlign


class TestAlign(unittest.TestCase):
    matrix = char_sub_matrix.get()

    def setUp(self) -> None:
        two_chars = {"aa": 0.0, "ab": -1.0, "bb": 0.0}
        self.line = LineAlign(two_chars, -1.0, -1.0)

    def test_align_01(self) -> None:
        self.assertEqual(self.line.align(["aba", "aba"]), ["aba", "aba"])

    def test_align_02(self) -> None:
        self.assertEqual(self.line.align(["aba", "aa"]), ["aba", "a⋄a"])

    def test_align_03(self) -> None:
        self.assertEqual(self.line.align(["aa", "aba"]), ["a⋄a", "aba"])

    def test_align_04(self) -> None:
        self.assertEqual(self.line.align(["aab", "aa"]), ["aab", "aa⋄"])

    def test_align_05(self) -> None:
        self.assertEqual(self.line.align(["baa", "aa"]), ["baa", "⋄aa"])

    def test_align_06(self) -> None:
        self.assertEqual(self.line.align(["aa", "baa"]), ["⋄aa", "baa"])

    def test_align_07(self) -> None:
        self.assertEqual(self.line.align(["aa", "aab"]), ["aa⋄", "aab"])

    def test_align_08(self) -> None:
        self.assertEqual(self.line.align(["aab", "baa"]), ["aab", "baa"])

    def test_align_09(self) -> None:
        self.assertEqual(self.line.align(["aab"]), ["aab"])

    def test_align_10(self) -> None:
        self.assertEqual(self.line.align([]), [])

    def test_align_11(self) -> None:
        self.assertEqual(self.line.align(["aab", "aaa", "aaa"]), ["aab", "aaa", "aaa"])

    def test_align_12(self) -> None:
        self.assertEqual(self.line.align(["aab", "abb", "aba"]), ["aab", "abb", "aba"])

    def test_align_13(self) -> None:
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
        # "R" over "T" is worth -1.0 in the default matrix, which is worse than
        # the two extra gaps it takes to leave "O" and "T" under each other.
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
        # With default gap=-3.0/skew=-0.5 the optimal alignment keeps the gap
        # block contiguous: "⋄⋄b" vs "abb" scores -3.5, while "⋄b⋄" scores -6.0.
        line = LineAlign({"aa": 0.0, "ab": -1.0, "bb": 0.0})
        self.assertEqual(line.align(["b", "abb"]), ["⋄⋄b", "abb"])

    def test_align_17(self) -> None:
        # The single "a" should sit under the last "a": a 3-gap block (-4.0)
        # beats a 2-gap block plus a trailing gap (-6.5).
        line = LineAlign({"aa": 0.0, "ab": -1.0, "bb": 0.0})
        self.assertEqual(line.align(["a", "bbaa"]), ["⋄⋄⋄a", "bbaa"])

    def test_align_18(self) -> None:
        # "ba" should align to the trailing "ba" of "ababb": one 3-gap block
        # (-4.0) plus one mismatch (-1.0) beats splitting the gap (-6.5).
        line = LineAlign({"aa": 0.0, "ab": -1.0, "bb": 0.0})
        self.assertEqual(line.align(["ba", "ababb"]), ["⋄⋄⋄ba", "ababb"])

    def test_align_19(self) -> None:
        # Same bug in progressive (3-line) mode.
        line = LineAlign({"aa": 0.0, "ab": -1.0, "bb": 0.0})
        self.assertEqual(line.align(["b", "abb", "abb"]), ["⋄⋄b", "abb", "abb"])
