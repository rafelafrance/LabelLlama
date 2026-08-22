from dataclasses import dataclass

from llama.llm_fields.llm_field import LlmField
from llama.pylib.base_field import BaseField


@dataclass
class DummyField(LlmField):
    value: str = ""

    def __post_init__(self, text: str) -> None:
        self.value = text


def test_llm_field_is_base_field() -> None:
    assert issubclass(LlmField, BaseField)


def test_text_is_not_a_field_name() -> None:
    assert "text" not in LlmField.get_field_names()


def test_llm_field_has_no_visible_fields() -> None:
    assert LlmField.get_visible_fields() == []


def test_subclass_receives_text_initvar() -> None:
    field = DummyField(text="source label text")
    assert field.value == "source label text"


def test_subclass_field_names_exclude_text() -> None:
    assert DummyField.get_field_names() == ["value"]


def test_default_score_exact_match() -> None:
    assert LlmField.score("abc", "abc", {}) == 1.0
