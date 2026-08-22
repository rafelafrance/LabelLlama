import importlib
from pathlib import Path

import pytest

from llama.calc_fields.calc_field import CalcField

FieldCase: type = tuple[Path, type[CalcField]]


def iter_field_cases() -> list[FieldCase]:
    cases = []
    for path in sorted(Path("llama/calc_fields").rglob("*.py")):
        if path.name in {"__init__.py", "calc_field.py"}:
            continue
        module_name = ".".join(path.with_suffix("").parts)
        class_name = path.stem[0].upper() + path.stem[1:]
        module = importlib.import_module(module_name)
        cases.append((path, getattr(module, class_name)))
    return cases


FIELD_CASES = iter_field_cases()


@pytest.mark.parametrize(("path", "field_class"), FIELD_CASES)
def test_calc_field_module_contract(path: Path, field_class: type[CalcField]) -> None:
    del path
    assert issubclass(field_class, CalcField)
    assert field_class.get_field_names()
    assert field_class.get_visible_fields() == field_class.get_field_names()
    assert "cleaned_rec" not in field_class.get_field_names()


@pytest.mark.parametrize(("path", "field_class"), FIELD_CASES)
def test_calc_field_classes_instantiate_with_cleaned_rec(
    path: Path,
    field_class: type[CalcField],
) -> None:
    del path
    field = field_class(cleaned_rec={})
    for field_name in field_class.get_field_names():
        assert hasattr(field, field_name)
