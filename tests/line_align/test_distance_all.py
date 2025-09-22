import unittest

from llama.line_align.levenshtein import Distance, levenshtein_all


class TestDistanceAll(unittest.TestCase):
    def test_distance_all_01(self) -> None:
        self.assertEqual(levenshtein_all(["aa", "bb"]), [Distance(2, 0, 1)])

    def test_distance_all_02(self) -> None:
        self.assertEqual(
            levenshtein_all(["aa", "bb", "ab"]),
            [Distance(1, 0, 2), Distance(1, 1, 2), Distance(2, 0, 1)],
        )

    def test_distance_all_03(self) -> None:
        self.assertEqual(
            levenshtein_all(
                [
                    "MOJAVE DESERT, PROVIDENCE MTS.: canyon above",
                    "E. MOJAVE DESERT , PROVIDENCE MTS . : canyon above",
                    "E MOJAVE DESERT PROVTDENCE MTS. # canyon above",
                    "Be ‘MOJAVE DESERT, PROVIDENCE canyon “above",
                ]
            ),
            [
                Distance(6, 0, 1),
                Distance(6, 0, 2),
                Distance(6, 1, 2),
                Distance(11, 0, 3),
                Distance(13, 1, 3),
                Distance(13, 2, 3),
            ],
        )
