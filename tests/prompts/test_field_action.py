from pathlib import Path
from types import SimpleNamespace

import pytest

from llama.calc_fields.location.elevation import Elevation
from llama.llm_fields.location.country import Country
from llama.prompts import field_action as field_action_module
from llama.prompts.field_action import FieldAction


def test_load_llm_field_action() -> None:
    action = FieldAction.load("../llama/llm_fields/location/country.py")

    assert action.name == "country"
    assert action.module == Path("../llama/llm_fields/location/country.py")
    assert action.columns == ["country"]
    assert action.field_class is Country


def test_load_calc_field_action_with_multiple_columns() -> None:
    action = FieldAction.load("../llama/calc_fields/location/elevation.py")

    assert action.name == "elevation"
    assert action.columns == [
        "elevation",
        "minimumElevationInMeters",
        "maximumElevationInMeters",
        "elevationUnits",
        "elevationEstimated",
    ]
    assert action.field_class is Elevation


def test_load_derives_module_name_from_prompt_link(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imported_modules = []

    class FakeField:
        def get_field_names(self) -> list[str]:
            return ["fakeField"]

    def fake_import_module(module_name: str) -> SimpleNamespace:
        imported_modules.append(module_name)
        return SimpleNamespace(FakeField=FakeField)

    monkeypatch.setattr(
        field_action_module.importlib,
        "import_module",
        fake_import_module,
    )

    action = FieldAction.load("../llama/llm_fields/fake/fakeField.py")

    assert imported_modules == ["llama.llm_fields.fake.fakeField"]
    assert action.name == "fakeField"
    assert action.columns == ["fakeField"]
    assert action.field_class is FakeField


def test_load_missing_module_raises_import_error() -> None:
    with pytest.raises(ImportError):
        FieldAction.load("../llama/llm_fields/missing/notAField.py")


def test_load_missing_class_raises_attribute_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_import_module(module_name: str) -> SimpleNamespace:
        del module_name
        return SimpleNamespace()

    monkeypatch.setattr(
        field_action_module.importlib,
        "import_module",
        fake_import_module,
    )

    with pytest.raises(AttributeError):
        FieldAction.load("../llama/llm_fields/fake/fakeField.py")
