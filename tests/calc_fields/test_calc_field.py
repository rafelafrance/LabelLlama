import inspect
import unittest
from dataclasses import dataclass, is_dataclass

from llama.calc_fields.calc_field import CalcField


def make_sample(**fields: str) -> type[CalcField]:
    """Minimal concrete subclass used to exercise the base class."""
    namespace = {"__annotations__": dict.fromkeys(fields, str)}
    namespace.update(fields)
    return dataclass(type("SampleField", (CalcField,), namespace))


SampleField = make_sample(alpha="", _hidden="")


class TestCalcField(unittest.TestCase):
    def test_calc_field_01(self) -> None:
        """CalcField is a dataclass so subclasses can inherit from it."""
        assert is_dataclass(CalcField)

    def test_calc_field_02(self) -> None:
        """Subclasses construct as (cleaned_rec, **field_values)."""
        field = SampleField({"a": 1}, "x")
        assert field.alpha == "x"

    def test_calc_field_03(self) -> None:
        """Cleaned_rec is the first init parameter (an InitVar)."""
        params = list(inspect.signature(CalcField).parameters)
        assert params[0] == "cleaned_rec"

    def test_calc_field_04(self) -> None:
        """Get_field_names returns the (stored) field names of a subclass."""
        assert SampleField.get_field_names() == ["alpha", "_hidden"]

    def test_calc_field_05(self) -> None:
        """Get_visible_fields excludes underscore-prefixed names."""
        assert SampleField.get_visible_fields() == ["alpha"]

    def test_calc_field_06(self) -> None:
        """ClassVars (scoring_method) are not reported as fields."""
        assert "scoring_method" not in SampleField.get_field_names()

    def test_calc_field_07(self) -> None:
        """The default scoring method for calc fields is LR."""
        assert CalcField.scoring_method == "LR"

    def test_calc_field_08(self) -> None:
        """Identical values score a perfect one."""
        assert CalcField.score("abc", "abc", {}) == 1.0

    def test_calc_field_09(self) -> None:
        """Score: surrounding whitespace is ignored."""
        assert CalcField.score(" abc ", "abc", {}) == 1.0

    def test_calc_field_10(self) -> None:
        """Score: values are stringified before comparison."""
        assert CalcField.score(1.5, "1.5", {}) == 1.0

    def test_calc_field_11(self) -> None:
        """Score: empty expect vs non-empty actual."""
        assert CalcField.score("", "abc", {}) == 0.0

    def test_calc_field_12(self) -> None:
        """Score: similar but different values score in between."""
        assert 0.0 < CalcField.score("abc", "abd", {}) < 1.0

    def test_calc_field_13(self) -> None:
        """InitVar fields (like cleaned_rec) are not part of the field list."""
        assert CalcField.get_field_names() == []


if __name__ == "__main__":
    unittest.main()
