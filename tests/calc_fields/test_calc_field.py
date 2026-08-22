from dataclasses import dataclass

from llama.calc_fields.calc_field import CalcField
from llama.pylib.base_field import BaseField


@dataclass
class DummyCalcField(CalcField):
    value: str = ""

    def __post_init__(self, cleaned_rec: dict | None) -> None:
        cleaned_rec = cleaned_rec or {}
        self.value = cleaned_rec.get("value", "")


def test_calc_field_is_base_field() -> None:
    assert issubclass(CalcField, BaseField)


def test_cleaned_rec_is_not_a_field_name() -> None:
    assert "cleaned_rec" not in CalcField.get_field_names()


def test_calc_field_has_no_visible_fields() -> None:
    assert CalcField.get_visible_fields() == []


def test_subclass_receives_cleaned_rec_initvar() -> None:
    field = DummyCalcField(cleaned_rec={"value": "calculated value"})
    assert field.value == "calculated value"


def test_subclass_field_names_exclude_cleaned_rec() -> None:
    assert DummyCalcField.get_field_names() == ["value"]


def test_default_score_exact_match() -> None:
    assert CalcField.score("abc", "abc", {}) == 1.0
