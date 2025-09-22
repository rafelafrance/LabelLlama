import unittest

from Levenshtein import distance


class TestDistance(unittest.TestCase):
    def test_distance_01(self) -> None:
        self.assertEqual(distance("aa", "bb"), 2)

    def test_distance_02(self) -> None:
        self.assertEqual(distance("ab", "bb"), 1)

    def test_distance_03(self) -> None:
        self.assertEqual(distance("ab", "ab"), 0)

    def test_distance_04(self) -> None:
        self.assertEqual(distance("aa", "aba"), 1)

    def test_distance_05(self) -> None:
        self.assertEqual(distance("aa", "baa"), 1)

    def test_distance_06(self) -> None:
        self.assertEqual(distance("aa", "aab"), 1)

    def test_distance_07(self) -> None:
        self.assertEqual(distance("baa", "aa"), 1)

    def test_distance_08(self) -> None:
        self.assertEqual(distance("aab", "aa"), 1)

    def test_distance_09(self) -> None:
        self.assertEqual(distance("baab", "aa"), 2)

    def test_distance_10(self) -> None:
        self.assertEqual(distance("aa", "baab"), 2)

    def test_distance_11(self) -> None:
        self.assertEqual(distance("", "aa"), 2)

    def test_distance_12(self) -> None:
        self.assertEqual(distance("aa", ""), 2)

    def test_distance_13(self) -> None:
        self.assertEqual(distance("", ""), 0)

    def test_distance_14(self) -> None:
        self.assertEqual(1, distance("aa", "五aa"))

    def test_distance_15(self) -> None:
        self.assertEqual(1, distance("五aa", "aa"))

    def test_distance_16(self) -> None:
        self.assertEqual(1, distance("aa", "aa五"))

    def test_distance_17(self) -> None:
        self.assertEqual(1, distance("aa五", "aa"))

    def test_distance_18(self) -> None:
        self.assertEqual(1, distance("a五a", "aa"))

    def test_distance_19(self) -> None:
        self.assertEqual(1, distance("aa", "a五a"))

    def test_distance_20(self) -> None:
        self.assertEqual(1, distance("五五", "五六"))

    def test_distance_21(self) -> None:
        self.assertEqual(0, distance("五五", "五五"))

    def test_distance_22(self) -> None:
        self.assertEqual(distance("123aa4", "aa"), 4)

    def test_distance_23(self) -> None:
        self.assertEqual(distance("aa", "1aa234"), 4)

    def test_distance_24(self) -> None:
        self.assertEqual(distance("aa", "a123a"), 3)

    def test_distance_25(self) -> None:
        self.assertEqual(distance("aa", "12345aa"), 5)

    def test_distance_26(self) -> None:
        self.assertEqual(
            distance("Commelinaceae Commelina virginica", "Commelina virginica"),
            14,
        )

    def test_distance_27(self) -> None:
        self.assertEqual(
            distance(
                "North Carolina NORTH CAROLINA Guilford County",
                "North Carolina OT CAROLINA Guilford County",
            ),
            3,
        )
