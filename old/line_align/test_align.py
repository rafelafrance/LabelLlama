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
                "⋄⋄⋄⋄MOJAVE DESERT⋄, PROVIDENCE MTS.⋄⋄: canyon ⋄above",
                "E⋄. MOJAVE DESERT , PROVIDENCE MTS . : canyon ⋄above",
                "E⋄⋄ MOJAVE DESERT ⋄⋄PROVTDENCE MTS. #⋄ canyon ⋄above",
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
                "North Carolina ⋄OT⋄⋄ CAROLINA Guilford County",
            ],
        )
