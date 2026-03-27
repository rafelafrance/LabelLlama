import unittest

from llama.common import fix_values


class TestFixValues(unittest.TestCase):
    # ---------------------------------------------------------------------
    def test_to_str_01(self) -> None:
        self.assertEqual(fix_values.to_str("test"), "test")

    def test_to_str_02(self) -> None:
        self.assertEqual(fix_values.to_str(11), "11")

    def test_to_str_03(self) -> None:
        self.assertEqual(fix_values.to_str(0.1), "0.1")

    def test_to_str_04(self) -> None:
        self.assertEqual(fix_values.to_str(value=True), "True")

    def test_to_str_05(self) -> None:
        self.assertEqual(fix_values.to_str(["one", "two"]), "one two")

    def test_to_str_06(self) -> None:
        self.assertEqual(fix_values.to_str(["one", "two"]), "one two")

    def test_to_str_07(self) -> None:
        self.assertEqual(fix_values.to_str([11, 22]), "11 22")

    def test_to_str_08(self) -> None:
        self.assertEqual(fix_values.to_str([0.1, 0.2]), "0.1 0.2")

    def test_to_str_09(self) -> None:
        self.assertEqual(fix_values.to_str([False, True]), "False True")

    def test_to_str_10(self) -> None:
        self.assertEqual(fix_values.to_str(object()), "")

    def test_to_str_11(self) -> None:
        self.assertEqual(fix_values.to_str(float("nan")), "")

    def test_to_str_12(self) -> None:
        self.assertEqual(fix_values.to_str(float("inf")), "")

    def test_to_str_13(self) -> None:
        self.assertEqual(fix_values.to_str(float("-inf")), "")

    # ---------------------------------------------------------------------
    def test_to_int_01(self) -> None:
        self.assertEqual(fix_values.to_int("test"), None)

    def test_to_int_02(self) -> None:
        self.assertEqual(fix_values.to_int(1), 1)

    def test_to_int_03(self) -> None:
        self.assertEqual(fix_values.to_int(1.4), 1)

    def test_to_int_04(self) -> None:
        self.assertEqual(fix_values.to_int(value=True), 1)

    def test_to_int_05(self) -> None:
        self.assertEqual(fix_values.to_int(object()), None)

    def test_to_int_06(self) -> None:
        self.assertEqual(fix_values.to_int(float("nan")), None)

    def test_to_int_07(self) -> None:
        self.assertEqual(fix_values.to_int(float("inf")), None)

    # ---------------------------------------------------------------------
    def test_to_float_01(self) -> None:
        self.assertEqual(fix_values.to_float("test"), None)

    def test_to_float_02(self) -> None:
        self.assertEqual(fix_values.to_float(1), 1.0)

    def test_to_float_03(self) -> None:
        self.assertEqual(fix_values.to_float(1.4), 1.4)

    def test_to_float_04(self) -> None:
        self.assertEqual(fix_values.to_float(value=True), 1.0)

    def test_to_float_05(self) -> None:
        self.assertEqual(fix_values.to_float(object()), None)

    def test_to_float_06(self) -> None:
        self.assertEqual(fix_values.to_float(float("nan")), None)

    def test_to_float_07(self) -> None:
        self.assertEqual(fix_values.to_float(float("inf")), None)

    # ---------------------------------------------------------------------
    def test_to_bool_01(self) -> None:
        self.assertEqual(fix_values.to_bool("test"), False)

    def test_to_bool_02(self) -> None:
        self.assertEqual(fix_values.to_bool(1), True)

    def test_to_bool_03(self) -> None:
        self.assertEqual(fix_values.to_bool(1.4), True)

    def test_to_bool_04(self) -> None:
        self.assertEqual(fix_values.to_bool(value=True), True)

    def test_to_bool_05(self) -> None:
        self.assertEqual(fix_values.to_bool(object()), True)

    def test_to_bool_06(self) -> None:
        self.assertEqual(fix_values.to_bool("TRUE"), True)

    def test_to_bool_07(self) -> None:
        self.assertEqual(fix_values.to_bool("Yes"), True)

    def test_to_bool_08(self) -> None:
        self.assertEqual(fix_values.to_bool("1"), True)

    def test_to_bool_09(self) -> None:
        self.assertEqual(fix_values.to_bool("0"), False)

    def test_to_bool_10(self) -> None:
        self.assertEqual(fix_values.to_bool(0), False)

    def test_to_bool_11(self) -> None:
        self.assertEqual(fix_values.to_bool(float("nan")), False)

    def test_to_bool_12(self) -> None:
        self.assertEqual(fix_values.to_bool(float("inf")), False)

    # ---------------------------------------------------------------------
    def test_to_list_of_strs_01(self) -> None:
        self.assertEqual(fix_values.to_list_of_strs("one"), ["one"])

    def test_to_list_of_strs_02(self) -> None:
        self.assertEqual(fix_values.to_list_of_strs(11), ["11"])

    def test_to_list_of_strs_03(self) -> None:
        self.assertEqual(
            fix_values.to_list_of_strs([1, 2.0, True, float("nan")]),
            ["1", "2.0", "True", ""],
        )

    def test_to_list_of_strs_04(self) -> None:
        self.assertEqual(fix_values.to_list_of_strs(object()), [])

    def test_to_list_of_strs_05(self) -> None:
        self.assertEqual(fix_values.to_list_of_strs([]), [])

    # ---------------------------------------------------------------------
    def test_to_list_of_ints_01(self) -> None:
        self.assertEqual(fix_values.to_list_of_ints("1,23"), [123])

    def test_to_list_of_ints_02(self) -> None:
        self.assertEqual(fix_values.to_list_of_ints(11), [11])

    def test_to_list_of_ints_03(self) -> None:
        self.assertEqual(
            fix_values.to_list_of_ints([1, 2.0, True, float("inf")]), [1, 2, 1]
        )

    def test_to_list_of_ints_04(self) -> None:
        self.assertEqual(fix_values.to_list_of_ints(object()), [])

    # ---------------------------------------------------------------------
    def test_to_list_of_floats_01(self) -> None:
        self.assertEqual(fix_values.to_list_of_floats("1,23.4"), [123.4])

    def test_to_list_of_floats_02(self) -> None:
        self.assertEqual(fix_values.to_list_of_floats(11), [11.0])

    def test_to_list_of_floats_03(self) -> None:
        self.assertEqual(
            fix_values.to_list_of_floats([1, 2.3, True, float("nan")]), [1.0, 2.3, 1.0]
        )

    def test_to_list_of_floats_04(self) -> None:
        self.assertEqual(fix_values.to_list_of_floats(object()), [])

    # ---------------------------------------------------------------------
    def test_str_to_float_01(self) -> None:
        self.assertEqual(fix_values.str_to_float("1,2,3.4"), 123.4)

    # ---------------------------------------------------------------------
    def test_str_to_int_01(self) -> None:
        self.assertEqual(fix_values.str_to_int("1,2,3.4"), 123)

    # ---------------------------------------------------------------------
    def test_stringified_list_01(self) -> None:
        self.assertEqual(fix_values.stringified_list("[1, 2]"), [1, 2])

    # ---------------------------------------------------------------------
    def test_clean_str_01(self) -> None:
        self.assertEqual(fix_values.clean_str("''"), "")

    def test_clean_str_02(self) -> None:
        self.assertEqual(fix_values.clean_str('""'), "")

    def test_clean_str_03(self) -> None:
        self.assertEqual(fix_values.clean_str("[]"), "")

    def test_clean_str_04(self) -> None:
        self.assertEqual(fix_values.clean_str("'test'"), "test")

    def test_clean_str_05(self) -> None:
        self.assertEqual(fix_values.clean_str('"test"'), "test")

    def test_clean_str_06(self) -> None:
        self.assertEqual(fix_values.clean_str('"test'), '"test')

    def test_clean_str_07(self) -> None:
        self.assertEqual(fix_values.clean_str('test"'), 'test"')
