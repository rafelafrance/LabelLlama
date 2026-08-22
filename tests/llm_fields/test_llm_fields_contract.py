import importlib
from pathlib import Path

import pytest

from llama.llm_fields.llm_field import LlmField

FieldCase: type = tuple[Path, type[LlmField]]


def iter_field_cases() -> list[FieldCase]:
    cases = []
    for path in sorted(Path("llama/llm_fields").rglob("*.py")):
        if path.name in {"__init__.py", "llm_field.py"}:
            continue
        module_name = ".".join(path.with_suffix("").parts)
        class_name = path.stem[0].upper() + path.stem[1:]
        module = importlib.import_module(module_name)
        cases.append((path, getattr(module, class_name)))
    return cases


FIELD_CASES = iter_field_cases()


@pytest.mark.parametrize(("path", "field_class"), FIELD_CASES)
def test_llm_field_module_contract(path: Path, field_class: type[LlmField]) -> None:
    assert issubclass(field_class, LlmField)
    assert field_class.get_field_names() == [path.stem]
    assert field_class.get_visible_fields() == [path.stem]
    assert "text" not in field_class.get_field_names()


@pytest.mark.parametrize(("path", "field_class"), FIELD_CASES)
def test_llm_field_descriptions_are_present(
    path: Path,
    field_class: type[LlmField],
) -> None:
    del path
    description = " ".join(field_class.description.split())
    assert description
    assert description.endswith(".")


@pytest.mark.parametrize(("path", "field_class"), FIELD_CASES)
def test_llm_field_classes_instantiate_with_source_text(
    path: Path,
    field_class: type[LlmField],
) -> None:
    field = field_class(text="source label text")
    assert hasattr(field, path.stem)
