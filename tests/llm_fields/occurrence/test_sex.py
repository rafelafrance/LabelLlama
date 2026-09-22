import unittest

from llama.llm_fields.occurrence.sex import Sex


class TestSex(unittest.TestCase):
    def test_sex_01(self) -> None:
        """Male notations normalize to "male"."""
        assert Sex("", "male").sex == "male"
        assert Sex("", "M").sex == "male"
        assert Sex("", "m").sex == "male"
        assert Sex("", "♂").sex == "male"
        assert Sex("", "MALE").sex == "male"

    def test_sex_02(self) -> None:
        """Female notations normalize to "female"."""
        assert Sex("", "female").sex == "female"
        assert Sex("", "F").sex == "female"
        assert Sex("", "f").sex == "female"
        assert Sex("", "♀").sex == "female"

    def test_sex_03(self) -> None:
        """Pair notations normalize to "male & female"."""
        assert Sex("", "♂♀").sex == "male & female"
        assert Sex("", "♀♂").sex == "male & female"
        assert Sex("", "pair").sex == "male & female"
        assert Sex("", "fm").sex == "male & female"
        assert Sex("", "mf").sex == "male & female"

    def test_sex_04(self) -> None:
        """A mixed male/female notation normalizes to "male & female"."""
        assert Sex("", "M and F").sex == "male & female"
        assert Sex("", "M/f").sex == "male & female"
        assert Sex("", "f/m").sex == "male & female"
        assert Sex("", "M F").sex == "male & female"

    def test_sex_05(self) -> None:
        """Empty input and empty-value notations stay empty."""
        assert Sex("", "").sex == ""
        assert Sex("", "none").sex == ""
        assert Sex("", "not present").sex == ""

    def test_sex_06(self) -> None:
        """Text with no male/female marker passes through unchanged."""
        assert Sex("", "unknown").sex == "unknown"
        assert Sex("", "intersex").sex == "intersex"
