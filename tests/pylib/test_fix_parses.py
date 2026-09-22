import unittest

from llama.llm_fields.location.verbatimLatitude import VerbatimLatitude
from llama.pylib.fix_parses import FixParses


class TestFixParses(unittest.TestCase):
    def setUp(self) -> None:
        self.fp = FixParses()

    # ---------------------------------------------------------------------
    def test_to_str_01(self) -> None:
        """A string passes through unchanged."""
        assert self.fp.to_str("test") == "test"

    def test_to_str_02(self) -> None:
        """An integer becomes its text."""
        assert self.fp.to_str(11) == "11"

    def test_to_str_03(self) -> None:
        """A float becomes its text."""
        assert self.fp.to_str(0.1) == "0.1"

    def test_to_str_04(self) -> None:
        """A boolean becomes its text."""
        assert self.fp.to_str(value=True) == "True"

    def test_to_str_06(self) -> None:
        """A list of strings is joined with spaces."""
        assert self.fp.to_str(["one", "two"]) == "one two"

    def test_to_str_07(self) -> None:
        """A list of integers is joined with spaces."""
        assert self.fp.to_str([11, 22]) == "11 22"

    def test_to_str_08(self) -> None:
        """A list of floats is joined with spaces."""
        assert self.fp.to_str([0.1, 0.2]) == "0.1 0.2"

    def test_to_str_09(self) -> None:
        """A list of booleans is joined with spaces."""
        assert self.fp.to_str([False, True]) == "False True"

    def test_to_str_10(self) -> None:
        """An object with no text becomes empty."""
        assert self.fp.to_str(object()) == ""

    def test_to_str_11(self) -> None:
        """NaN becomes empty text."""
        assert self.fp.to_str(float("nan")) == ""

    def test_to_str_12(self) -> None:
        """Infinity becomes empty text."""
        assert self.fp.to_str(float("inf")) == ""

    def test_to_str_13(self) -> None:
        """Negative infinity becomes empty text."""
        assert self.fp.to_str(float("-inf")) == ""

    # ---------------------------------------------------------------------
    def test_to_int_14(self) -> None:
        """Text with no digits is not an int."""
        assert self.fp.to_int("test") is None

    def test_to_int_15(self) -> None:
        """An integer passes through."""
        assert self.fp.to_int(1) == 1

    def test_to_int_16(self) -> None:
        """A float is truncated to its whole part."""
        assert self.fp.to_int(1.4) == 1

    def test_to_int_17(self) -> None:
        """True is counted as one."""
        assert self.fp.to_int(value=True) == 1

    def test_to_int_18(self) -> None:
        """An object with no digits is not an int."""
        assert self.fp.to_int(object()) is None

    def test_to_int_19(self) -> None:
        """NaN is not an int."""
        assert self.fp.to_int(float("nan")) is None

    def test_to_int_20(self) -> None:
        """Infinity is not an int."""
        assert self.fp.to_int(float("inf")) is None

    def test_to_int_21(self) -> None:
        """A negative integer passes through."""
        assert self.fp.to_int(-1) == -1

    # ---------------------------------------------------------------------
    def test_to_float_22(self) -> None:
        """Text with no number is not a float."""
        assert self.fp.to_float("test") is None

    def test_to_float_23(self) -> None:
        """An integer becomes a float."""
        assert self.fp.to_float(1) == 1.0

    def test_to_float_24(self) -> None:
        """A float passes through."""
        assert self.fp.to_float(1.4) == 1.4

    def test_to_float_25(self) -> None:
        """True becomes one point zero."""
        assert self.fp.to_float(value=True) == 1.0

    def test_to_float_26(self) -> None:
        """An object with no number is not a float."""
        assert self.fp.to_float(object()) is None

    def test_to_float_27(self) -> None:
        """NaN is not a float."""
        assert self.fp.to_float(float("nan")) is None

    def test_to_float_28(self) -> None:
        """Infinity is not a float."""
        assert self.fp.to_float(float("inf")) is None

    def test_to_float_29(self) -> None:
        """A negative float passes through."""
        assert self.fp.to_float(-1.4) == -1.4

    # ---------------------------------------------------------------------
    def test_to_bool_30(self) -> None:
        """Text that is not a yes word is false."""
        assert self.fp.to_bool("test") is False

    def test_to_bool_31(self) -> None:
        """One is true."""
        assert self.fp.to_bool(1) is True

    def test_to_bool_32(self) -> None:
        """A non-zero number is true."""
        assert self.fp.to_bool(1.4) is True

    def test_to_bool_33(self) -> None:
        """A boolean passes through."""
        assert self.fp.to_bool(value=True) is True

    def test_to_bool_34(self) -> None:
        """Any object with no text is true."""
        assert self.fp.to_bool(object()) is True

    def test_to_bool_35(self) -> None:
        """An upper case TRUE is true."""
        assert self.fp.to_bool("TRUE") is True

    def test_to_bool_36(self) -> None:
        """A capitalized Yes is true."""
        assert self.fp.to_bool("Yes") is True

    def test_to_bool_37(self) -> None:
        """The digit one is true."""
        assert self.fp.to_bool("1") is True

    def test_to_bool_38(self) -> None:
        """The digit zero is false."""
        assert self.fp.to_bool("0") is False

    def test_to_bool_39(self) -> None:
        """Zero is false."""
        assert self.fp.to_bool(0) is False

    def test_to_bool_40(self) -> None:
        """NaN is false."""
        assert self.fp.to_bool(float("nan")) is False

    def test_to_bool_41(self) -> None:
        """Infinity is false even though bool() says true."""
        assert self.fp.to_bool(float("inf")) is False

    # ---------------------------------------------------------------------
    def test_to_list_of_strs_42(self) -> None:
        """A single string becomes a one item list."""
        assert self.fp.to_list_of_strs("one") == ["one"]

    def test_to_list_of_strs_43(self) -> None:
        """A number becomes a list of its text."""
        assert self.fp.to_list_of_strs(11) == ["11"]

    def test_to_list_of_strs_44(self) -> None:
        """A list converts item by item, NaN becoming empty."""
        assert self.fp.to_list_of_strs([1, 2.0, True, float("nan")]) == [
            "1",
            "2.0",
            "True",
            "",
        ]

    def test_to_list_of_strs_45(self) -> None:
        """An object with no text gives no items."""
        assert self.fp.to_list_of_strs(object()) == []

    def test_to_list_of_strs_46(self) -> None:
        """An empty list stays empty."""
        assert self.fp.to_list_of_strs([]) == []

    # ---------------------------------------------------------------------
    def test_to_list_of_ints_47(self) -> None:
        """Thousands separators do not break the int."""
        assert self.fp.to_list_of_ints("1,23") == [123]

    def test_to_list_of_ints_48(self) -> None:
        """A single number becomes a one item list."""
        assert self.fp.to_list_of_ints(11) == [11]

    def test_to_list_of_ints_49(self) -> None:
        """A list converts item by item, inf being dropped."""
        assert self.fp.to_list_of_ints([1, 2.0, True, float("inf")]) == [1, 2, 1]

    def test_to_list_of_ints_50(self) -> None:
        """An object with no digits gives no items."""
        assert self.fp.to_list_of_ints(object()) == []

    # ---------------------------------------------------------------------
    def test_to_list_of_floats_51(self) -> None:
        """Thousands separators do not break the float."""
        assert self.fp.to_list_of_floats("1,23.4") == [123.4]

    def test_to_list_of_floats_52(self) -> None:
        """A single number becomes a one item list."""
        assert self.fp.to_list_of_floats(11) == [11.0]

    def test_to_list_of_floats_53(self) -> None:
        """A list converts item by item, NaN being dropped."""
        assert self.fp.to_list_of_floats([1, 2.3, True, float("nan")]) == [
            1.0,
            2.3,
            1.0,
        ]

    def test_to_list_of_floats_54(self) -> None:
        """An object with no number gives no items."""
        assert self.fp.to_list_of_floats(object()) == []

    # ---------------------------------------------------------------------
    def test_str_to_float_55(self) -> None:
        """Commas are stripped before the float is read."""
        assert self.fp.str_to_float("1,2,3.4") == 123.4

    # ---------------------------------------------------------------------
    def test_str_to_int_56(self) -> None:
        """Commas are stripped before the int is read."""
        assert self.fp.str_to_int("1,2,3.4") == 123

    # ---------------------------------------------------------------------
    def test_stringified_list_57(self) -> None:
        """A stringified list is parsed back into items."""
        assert self.fp.stringified_list("[1, 2]") == [1, 2]

    # ---------------------------------------------------------------------
    def test_clean_str_58(self) -> None:
        """Empty single quotes are no value."""
        assert self.fp.clean_str("''") == ""

    def test_clean_str_59(self) -> None:
        """Empty double quotes are no value."""
        assert self.fp.clean_str('""') == ""

    def test_clean_str_60(self) -> None:
        """An empty list in text is no value."""
        assert self.fp.clean_str("[]") == ""

    def test_clean_str_61(self) -> None:
        """Surrounding single quotes are removed."""
        assert self.fp.clean_str("'test'") == "test"

    def test_clean_str_62(self) -> None:
        """Surrounding double quotes are removed."""
        assert self.fp.clean_str('"test"') == "test"

    def test_clean_str_63(self) -> None:
        """An opening quote with no match is left alone."""
        assert self.fp.clean_str('"test') == '"test'

    def test_clean_str_64(self) -> None:
        """A closing quote with no match is left alone."""
        assert self.fp.clean_str('test"') == 'test"'

    # ---------------------------------------------------------------------
    def test_date_to_iso_65(self) -> None:
        """A roman month name becomes its month number."""
        assert self.fp.date_to_iso("01/ix-77") == "1977-09-01"

    def test_date_to_iso_66(self) -> None:
        """A roman month and year give a year-month date."""
        assert self.fp.date_to_iso("ix-77") == "1977-09"

    def test_date_to_iso_67(self) -> None:
        """Two bare numbers are not read as a date."""
        assert self.fp.date_to_iso("09-77") == ""

    def test_date_to_iso_68(self) -> None:
        """A month name with day and year is converted."""
        assert self.fp.date_to_iso("Jan 30, 1922") == "1922-01-30"

    def test_date_to_iso_69(self) -> None:
        """A month name and year give a year-month date."""
        assert self.fp.date_to_iso("August 1911") == "1911-08"

    # ---------------------------------------------------------------------
    def test_hallucinated_str_70(self) -> None:
        """A value found in the OCR text is kept."""
        assert self.fp.hallucinated_str("TEST", "words test more words") == "TEST"

    def test_hallucinated_str_71(self) -> None:
        """A value missing from the OCR text is dropped."""
        assert self.fp.hallucinated_str("TEST", "words and more words") == ""

    def test_hallucinated_str_72(self) -> None:
        """A multi-word value is matched as a phrase."""
        assert (
            self.fp.hallucinated_str(
                "Atongan River",
                "Katanglad Mts Atongan River October 1991",
            )
            == "Atongan River"
        )

    # ---------------------------------------------------------------------
    def test_clean_punct_73(self) -> None:
        """Brackets around a word are removed."""
        assert self.fp.clean_punct("[word]") == "word"

    def test_clean_punct_74(self) -> None:
        """Quotes inside the parentheses are removed too."""
        assert self.fp.clean_punct("('word')") == "word"

    def test_clean_punct_76(self) -> None:
        """Braces and quotes are cleaned."""
        assert self.fp.clean_punct("{'word'}") == "word"

    # ---------------------------------------------------------------------
    def test_empty_noted_with_field_name_77(self) -> None:
        """Repeating the field name means empty."""
        lat = VerbatimLatitude(verbatimLatitude="verbatimLatitude")
        assert lat.verbatimLatitude == ""

    def test_empty_noted_with_field_name_78(self) -> None:
        """A parenthesized field name means empty."""
        lat = VerbatimLatitude(verbatimLatitude="(verbatimLatitude)")
        assert lat.verbatimLatitude == ""

    def test_empty_noted_with_field_name_79(self) -> None:
        """A bracketed field name means empty."""
        lat = VerbatimLatitude(verbatimLatitude="[verbatimLatitude]")
        assert lat.verbatimLatitude == ""

    def test_empty_noted_with_field_name_80(self) -> None:
        """A braced field name means empty."""
        lat = VerbatimLatitude(verbatimLatitude="{verbatimLatitude}")
        assert lat.verbatimLatitude == ""

    def test_empty_noted_with_field_name_81(self) -> None:
        """A value that is not the field name is kept."""
        lat = VerbatimLatitude(verbatimLatitude="hello")
        assert lat.verbatimLatitude == "hello"

    # ---------------------------------------------------------------------
    def test_normalize_decimal_comma_82(self) -> None:
        """A decimal comma becomes a decimal point."""
        assert self.fp.normalize_decimal_comma("45,5") == "45.5"

    def test_normalize_decimal_comma_83(self) -> None:
        """A one digit decimal keeps its precision."""
        assert self.fp.normalize_decimal_comma("4,5") == "4.5"

    def test_normalize_decimal_comma_84(self) -> None:
        """A negative decimal comma is converted."""
        assert self.fp.normalize_decimal_comma("-120,25") == "-120.25"

    def test_normalize_decimal_comma_85(self) -> None:
        """A trailing non-digit suffix (hemisphere, units) is preserved."""
        assert self.fp.normalize_decimal_comma("45,5 N") == "45.5 N"

    def test_normalize_decimal_comma_86(self) -> None:
        """A dot in the value means the comma is a thousands separator."""
        assert self.fp.normalize_decimal_comma("1,234.5") == "1,234.5"

    def test_normalize_decimal_comma_87(self) -> None:
        """Two commas are a thousands-separator chain; leave it alone."""
        assert self.fp.normalize_decimal_comma("1,234,567") == "1,234,567"

    def test_normalize_decimal_comma_88(self) -> None:
        """Text with a decimal point is unchanged."""
        assert self.fp.normalize_decimal_comma("45.5") == "45.5"

    def test_normalize_decimal_comma_89(self) -> None:
        """Empty text stays empty."""
        assert self.fp.normalize_decimal_comma("") == ""

    # ---------------------------------------------------------------------
    def test_date_to_iso_extra_90(self) -> None:
        """Roman-numeral month (viii = August)."""
        assert self.fp.date_to_iso("viii 1990") == "1990-08"

    def test_date_to_iso_extra_91(self) -> None:
        """A future date is shifted back 100 years."""
        assert self.fp.date_to_iso("2030-01-15") == "1930-01-15"

    def test_date_to_iso_extra_92(self) -> None:
        """A year on its own is already an ISO date."""
        assert self.fp.date_to_iso("1990") == "1990"

    # ---------------------------------------------------------------------
    def test_title_with_exceptions_93(self) -> None:
        """Small words stay lowercase but not first."""
        assert (
            FixParses.title_with_exceptions("the man and the woman")
            == "The Man and the Woman"
        )

    def test_title_with_exceptions_94(self) -> None:
        """A place name keeps its own small words."""
        assert (
            FixParses.title_with_exceptions("river de la plata") == "River de La Plata"
        )

    # ---------------------------------------------------------------------
    def test_to_truthy_95(self) -> None:
        """Yes is true."""
        assert self.fp.to_truthy("yes") is True

    def test_to_truthy_96(self) -> None:
        """Falsy values yield "" rather than False."""
        assert self.fp.to_truthy("no") == ""

    def test_to_truthy_97(self) -> None:
        """One is true."""
        assert self.fp.to_truthy(1) is True

    def test_to_truthy_98(self) -> None:
        """Zero is empty rather than false."""
        assert self.fp.to_truthy(0) == ""

    # ---------------------------------------------------------------------
    def test_reduce_list_99(self) -> None:
        """A one item list reduces to its item."""
        assert self.fp.reduce_list([]) == []
        assert self.fp.reduce_list([1]) == 1
        assert self.fp.reduce_list([1, 2]) == [1, 2]

    def test_reduce_str_list_100(self) -> None:
        """A one item string list reduces to its string."""
        assert self.fp.reduce_str_list("") == ""
        assert self.fp.reduce_str_list(["a"]) == "a"

    def test_reduce_str_list_101(self) -> None:
        """Multiple items are returned as a comma joined list."""
        assert self.fp.reduce_str_list(["a", "b"]) == "a, b"

    # ---------------------------------------------------------------------
    def test_to_int_extra_102(self) -> None:
        """The first integer is extracted from surrounding text."""
        assert self.fp.to_int("abc 12") == 12

    def test_to_int_extra_103(self) -> None:
        """The integer part is taken from a decimal string."""
        assert self.fp.to_int("1.5") == 1

    def test_to_int_extra_104(self) -> None:
        """A one item list becomes that int, others are None."""
        assert self.fp.to_int([5]) == 5
        assert self.fp.to_int([]) is None
        assert self.fp.to_int(None) is None

    # ---------------------------------------------------------------------
    def test_to_float_extra_105(self) -> None:
        """A number is read out of surrounding text."""
        assert self.fp.to_float(".5") == 0.5
        assert self.fp.to_float("abc 3.5") == 3.5
        assert self.fp.to_float(None) is None

    def test_to_float_extra_106(self) -> None:
        """Repeated dots are not a valid number."""
        assert self.fp.to_float("1.2.3") is None

    # ---------------------------------------------------------------------
    def test_to_bool_extra_107(self) -> None:
        """On and off are read as booleans."""
        assert self.fp.to_bool("on") is True
        assert self.fp.to_bool("off") is False

    # ---------------------------------------------------------------------
    def test_to_list_of_ints_extra_108(self) -> None:
        """A dashed range yields both values (no negative)."""
        assert self.fp.to_list_of_ints("12-34") == [12, 34]

    def test_to_list_of_floats_extra_109(self) -> None:
        """Space separated numbers become a float list."""
        assert self.fp.to_list_of_floats("1.5 2.5") == [1.5, 2.5]

    def test_to_list_of_floats_extra_110(self) -> None:
        """A malformed number gives an empty list."""
        assert self.fp.to_list_of_floats("1.2.3") == []

    # ---------------------------------------------------------------------
    def test_str_to_float_extra_111(self) -> None:
        """A malformed number is not a float."""
        assert self.fp.str_to_float(".5") == 0.5
        assert self.fp.str_to_float("-2.5") == -2.5
        assert self.fp.str_to_float("abc") is None
        assert self.fp.str_to_float("1.2.3") is None

    def test_str_to_int_extra_112(self) -> None:
        """A negative int is read from text."""
        assert self.fp.str_to_int("-5") == -5
        assert self.fp.str_to_int("abc") is None

    # ---------------------------------------------------------------------
    def test_stringified_list_extra_113(self) -> None:
        """A stringified list of strings is parsed."""
        assert self.fp.stringified_list("['a', 'b']") == ["a", "b"]

    def test_stringified_list_extra_114(self) -> None:
        """Text that is not a list is returned unchanged."""
        assert self.fp.stringified_list("not a list") == "not a list"

    # ---------------------------------------------------------------------
    def test_clean_str_extra_115(self) -> None:
        """Surrounding brackets of any kind are stripped."""
        assert self.fp.clean_str("(test)") == "test"
        assert self.fp.clean_str("[test]") == "test"
        assert self.fp.clean_str("{test}") == "test"

    def test_clean_str_extra_116(self) -> None:
        """Markdown bold / italic notations are removed."""
        assert self.fp.clean_str("**test**") == "test"
        assert self.fp.clean_str("_test_") == "test"

    def test_clean_str_extra_117(self) -> None:
        """Empty-field notations (case-insensitive) become ""."""
        assert self.fp.clean_str("NAN") == ""
        assert self.fp.clean_str("(blank)") == ""
        assert self.fp.clean_str("{none}") == ""
        assert self.fp.clean_str("[not specified]") == ""
        assert self.fp.clean_str("not present") == ""

    # ---------------------------------------------------------------------
    def test_to_str_extra_118(self) -> None:
        """Empty/cleaned-empty items are dropped when joining a list."""
        assert self.fp.to_str(["", "two"]) == "two"
        assert self.fp.to_str(None) == ""
