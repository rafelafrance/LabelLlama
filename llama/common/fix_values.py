"""Fix common problems with values after a language model mangles them."""

import contextlib
import json
import re
from typing import Any

INT = re.compile(r"\d+")
FLOAT = re.compile(r" (\d+(\.\d*)? | \.\d+ )", flags=re.VERBOSE)


def to_str(value: Any) -> str:
    match type(value):
        case str():
            return clean_str(value)
        case int() | float() | bool():
            return str(value)
        case list() if value[0] is str:
            return " ".join(c for v in value if (c := clean_str(v)))
        case list():
            return " ".join(str(v) for v in value)
        case _:
            return ""


def to_int(value: Any) -> int | None:
    value = list_to_item(value)

    match type(value):
        case str():
            return str_to_int(value)
        case _:
            return int(value)


def to_float(value: Any) -> float | None:
    value = list_to_item(value)

    match type(value):
        case str():
            return str_to_float(value)
        case _:
            return float(value)


def to_bool(value: Any) -> bool:
    value = list_to_item(value)

    match type(value):
        case str():
            return value.lower() in ("true", "yes", "1")
        case _:
            return bool(value)


def to_list_of_strs(value: Any) -> list[str]:
    value = str_to_list(value)

    match type(value):
        case str() | int() | float() | bool():
            return [str(value)]
        case list():
            return [str(v) for v in value]
        case _:
            return []


def to_list_of_ints(value: Any) -> list[int]:
    value = str_to_list(value)

    match type(value):
        case str() | int() | float() | bool():
            return [int(value)]
        case list() if value[0] is str:
            return [c for v in value if (c := str_to_int(v))]
        case list():
            return [i for v in value if (i := int(v))]
        case _:
            return []


def to_list_of_floats(value: Any) -> list[float]:
    value = str_to_list(value)

    match type(value):
        case str() | int() | float() | bool():
            return [float(value)]
        case list() if value[0] is str:
            return [f for v in value if (f := str_to_float(v))]
        case list():
            return [f for v in value if (f := float(v))]
        case _:
            return []


def str_to_float(value: str) -> float | None:
    value = re.sub(r",", "", value)
    m = FLOAT.search(value)
    return float(m[0]) if m else None


def str_to_int(value: str) -> int | None:
    value = re.sub(r",", "", value)
    m = INT.search(value)
    return int(m[0]) if m else None


def str_to_list(value: Any) -> list[Any] | Any:
    if value is str:
        value = clean_str(value)
        value = stringified_list(value)
    return value


def stringified_list(value: str) -> list[Any] | str:
    if value.startswith("[") and value.endswith("]"):
        if len(value) > 1 and value[1] == "'":
            value = value.replace('"', r"\"")
            value = value.replace("'", '"')

        with contextlib.suppress(json.decoder.JSONDecodeError):
            value = json.loads(value)

    return value


def clean_str(value: str) -> str:
    # Notations for an empty field
    if value in ("[]", '""', "''"):
        return ""

    # Remove leading and trailing quotes
    value = re.sub(r'"(.+)"', r"\1", value)
    value = re.sub(r"'(.+)'", r"\1", value)

    return value


def list_to_item(value: Any) -> Any:
    value = value[0] if value is list and len(value) > 0 else value
    value = None if value is list and len(value) == 0 else value
    return value
