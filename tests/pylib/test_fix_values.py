import unittest

from llama.pylib import fix_values


class TestFixValues(unittest.TestCase):
    # ---------------------------------------------------------------------
    def test_to_str_01(self) -> None:
        assert fix_values.to_str("test") == "test"

    def test_to_str_02(self) -> None:
        assert fix_values.to_str(11) == "11"

    def test_to_str_03(self) -> None:
        assert fix_values.to_str(0.1) == "0.1"

    def test_to_str_04(self) -> None:
        assert fix_values.to_str(value=True) == "True"

    def test_to_str_05(self) -> None:
        assert fix_values.to_str(["one", "two"]) == "one two"

    def test_to_str_06(self) -> None:
        assert fix_values.to_str(["one", "two"]) == "one two"

    def test_to_str_07(self) -> None:
        assert fix_values.to_str([11, 22]) == "11 22"

    def test_to_str_08(self) -> None:
        assert fix_values.to_str([0.1, 0.2]) == "0.1 0.2"

    def test_to_str_09(self) -> None:
        assert fix_values.to_str([False, True]) == "False True"

    def test_to_str_10(self) -> None:
        assert fix_values.to_str(object()) == ""

    def test_to_str_11(self) -> None:
        assert fix_values.to_str(float("nan")) == ""

    def test_to_str_12(self) -> None:
        assert fix_values.to_str(float("inf")) == ""

    def test_to_str_13(self) -> None:
        assert fix_values.to_str(float("-inf")) == ""

    # ---------------------------------------------------------------------
    def test_to_int_01(self) -> None:
        assert fix_values.to_int("test") is None

    def test_to_int_02(self) -> None:
        assert fix_values.to_int(1) == 1

    def test_to_int_03(self) -> None:
        assert fix_values.to_int(1.4) == 1

    def test_to_int_04(self) -> None:
        assert fix_values.to_int(value=True) == 1

    def test_to_int_05(self) -> None:
        assert fix_values.to_int(object()) is None

    def test_to_int_06(self) -> None:
        assert fix_values.to_int(float("nan")) is None

    def test_to_int_07(self) -> None:
        assert fix_values.to_int(float("inf")) is None

    # ---------------------------------------------------------------------
    def test_to_float_01(self) -> None:
        assert fix_values.to_float("test") is None

    def test_to_float_02(self) -> None:
        assert fix_values.to_float(1) == 1.0

    def test_to_float_03(self) -> None:
        assert fix_values.to_float(1.4) == 1.4

    def test_to_float_04(self) -> None:
        assert fix_values.to_float(value=True) == 1.0

    def test_to_float_05(self) -> None:
        assert fix_values.to_float(object()) is None

    def test_to_float_06(self) -> None:
        assert fix_values.to_float(float("nan")) is None

    def test_to_float_07(self) -> None:
        assert fix_values.to_float(float("inf")) is None

    # ---------------------------------------------------------------------
    def test_to_bool_01(self) -> None:
        assert fix_values.to_bool("test") is False

    def test_to_bool_02(self) -> None:
        assert fix_values.to_bool(1) is True

    def test_to_bool_03(self) -> None:
        assert fix_values.to_bool(1.4) is True

    def test_to_bool_04(self) -> None:
        assert fix_values.to_bool(value=True) is True

    def test_to_bool_05(self) -> None:
        assert fix_values.to_bool(object()) is True

    def test_to_bool_06(self) -> None:
        assert fix_values.to_bool("TRUE") is True

    def test_to_bool_07(self) -> None:
        assert fix_values.to_bool("Yes") is True

    def test_to_bool_08(self) -> None:
        assert fix_values.to_bool("1") is True

    def test_to_bool_09(self) -> None:
        assert fix_values.to_bool("0") is False

    def test_to_bool_10(self) -> None:
        assert fix_values.to_bool(0) is False

    def test_to_bool_11(self) -> None:
        assert fix_values.to_bool(float("nan")) is False

    def test_to_bool_12(self) -> None:
        assert fix_values.to_bool(float("inf")) is False

    # ---------------------------------------------------------------------
    def test_to_list_of_strs_01(self) -> None:
        assert fix_values.to_list_of_strs("one") == ["one"]

    def test_to_list_of_strs_02(self) -> None:
        assert fix_values.to_list_of_strs(11) == ["11"]

    def test_to_list_of_strs_03(self) -> None:
        assert (
            fix_values.to_list_of_strs([1, 2.0, True, float("nan")])
            == ["1", "2.0", "True", ""]
        )

    def test_to_list_of_strs_04(self) -> None:
        assert fix_values.to_list_of_strs(object()) == []

    def test_to_list_of_strs_05(self) -> None:
        assert fix_values.to_list_of_strs([]) == []

    # ---------------------------------------------------------------------
    def test_to_list_of_ints_01(self) -> None:
        assert fix_values.to_list_of_ints("1,23") == [123]

    def test_to_list_of_ints_02(self) -> None:
        assert fix_values.to_list_of_ints(11) == [11]

    def test_to_list_of_ints_03(self) -> None:
        assert (
            fix_values.to_list_of_ints([1, 2.0, True, float("inf")]) == [1, 2, 1]
        )

    def test_to_list_of_ints_04(self) -> None:
        assert fix_values.to_list_of_ints(object()) == []

    # ---------------------------------------------------------------------
    def test_to_list_of_floats_01(self) -> None:
        assert fix_values.to_list_of_floats("1,23.4") == [123.4]

    def test_to_list_of_floats_02(self) -> None:
        assert fix_values.to_list_of_floats(11) == [11.0]

    def test_to_list_of_floats_03(self) -> None:
        assert (
            fix_values.to_list_of_floats([1, 2.3, True, float("nan")])
            == [1.0, 2.3, 1.0]
        )

    def test_to_list_of_floats_04(self) -> None:
        assert fix_values.to_list_of_floats(object()) == []

    # ---------------------------------------------------------------------
    def test_str_to_float_01(self) -> None:
        assert fix_values.str_to_float("1,2,3.4") == 123.4

    # ---------------------------------------------------------------------
    def test_str_to_int_01(self) -> None:
        assert fix_values.str_to_int("1,2,3.4") == 123

    # ---------------------------------------------------------------------
    def test_stringified_list_01(self) -> None:
        assert fix_values.stringified_list("[1, 2]") == [1, 2]

    # ---------------------------------------------------------------------
    def test_clean_str_01(self) -> None:
        assert fix_values.clean_str("''") == ""

    def test_clean_str_02(self) -> None:
        assert fix_values.clean_str('""') == ""

    def test_clean_str_03(self) -> None:
        assert fix_values.clean_str("[]") == ""

    def test_clean_str_04(self) -> None:
        assert fix_values.clean_str("'test'") == "test"

    def test_clean_str_05(self) -> None:
        assert fix_values.clean_str('"test"') == "test"

    def test_clean_str_06(self) -> None:
        assert fix_values.clean_str('"test') == '"test'

    def test_clean_str_07(self) -> None:
        assert fix_values.clean_str('test"') == 'test"'

    # ---------------------------------------------------------------------
    def test_date_to_iso_01(self) -> None:
        assert fix_values.date_to_iso("01/ix-77") == "1977-09-01"

    def test_date_to_iso_02(self) -> None:
        assert fix_values.date_to_iso("ix-77") == "1977-09"

    def test_date_to_iso_03(self) -> None:
        assert fix_values.date_to_iso("09-77") == ""

    def test_date_to_iso_04(self) -> None:
        assert fix_values.date_to_iso("Jan 30, 1922") == "1922-01-30"

    def test_date_to_iso_05(self) -> None:
        assert fix_values.date_to_iso("August 1911") == "1911-08"

    # ---------------------------------------------------------------------
    def test_hallucinated_str_01(self) -> None:
        assert fix_values.hallucinated_str("TEST", "words test more words") == "TEST"

    def test_hallucinated_str_02(self) -> None:
        assert fix_values.hallucinated_str("TEST", "words and more words") == ""

    def test_hallucinated_str_03(self) -> None:
        assert fix_values.hallucinated_str(
            "Atongan River",
            "Katanglad Mts Atongan River October 1991",
        ) == "Atongan River"

    # ---------------------------------------------------------------------
    def test_remove_leading_punct_01(self) -> None:
        assert fix_values.remove_leading_punct("[word]") == "word]"

    def test_remove_leading_punct_02(self) -> None:
        assert fix_values.remove_leading_punct("['word']") == "word']"

    # ---------------------------------------------------------------------
    def test_remove_trailing_punct_01(self) -> None:
        assert fix_values.remove_trailing_punct("['word']") == "['word"

    # ---------------------------------------------------------------------
    def test_clean_str_ends_01(self) -> None:
        assert fix_values.clean_str_ends("['word']") == "word"
