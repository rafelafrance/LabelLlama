"""Fix common problems with values after a language model mangles them."""

import contextlib
import json
import re
from calendar import IllegalMonthError
from typing import Any

from dateutil import parser

INT = re.compile(r"\d+")
FLOAT = re.compile(r" (?: \d+ (?: \.\d* )? | \.\d+ )", flags=re.VERBOSE)


def to_str(value: Any) -> str:
    match value:
        case str():
            return clean_str(value)
        case int() | float() | bool():
            return str(value)
        case list() if len(value) > 0 and isinstance(value[0], str):
            return " ".join(c for v in value if (c := clean_str(v)))
        case list():
            return " ".join(str(v) for v in value)
        case _:
            return ""


def to_int(value: Any) -> int | None:
    value = list_to_item(value)

    match value:
        case str():
            value = clean_str(value)
            return str_to_int(value)
        case int() | float() | bool():
            return int(value)
        case _:
            return None


def to_float(value: Any) -> float | None:
    value = list_to_item(value)

    match value:
        case str():
            value = clean_str(value)
            return str_to_float(value)
        case int() | float() | bool():
            return float(value)
        case _:
            return None


def to_bool(value: Any) -> bool:
    value = list_to_item(value)

    match value:
        case str():
            value = clean_str(value)
            return value.lower() in ("true", "yes", "1", "on")
        case _:
            return bool(value)


def to_list_of_strs(value: Any) -> list[str]:
    value = str_to_list(value)

    match value:
        case str():
            value = clean_str(value)
            return [value] if value else []
        case int() | float() | bool():
            return [str(value)]
        case list() if len(value) > 0:
            return [str(v) for v in value if v]
        case _:
            return []


def to_list_of_ints(value: Any) -> list[int]:
    value = str_to_list(value)

    match value:
        case str():
            value = re.sub(r",", "", value)
            return [int(v) for v in INT.findall(value)]
        case int() | float() | bool():
            return [int(value)]
        case list() if len(value) > 1 and isinstance(value[0], str):
            return [c for v in value if (c := str_to_int(v))]
        case list() if len(value) > 0:
            return [i for v in value if (i := int(v))]
        case _:
            return []


def to_list_of_floats(value: Any) -> list[float]:
    value = str_to_list(value)

    match value:
        case str():
            value = re.sub(r",", "", value)
            return [float(v) for v in FLOAT.findall(value)]
        case int() | float() | bool():
            return [float(value)]
        case list() if len(value) > 0 and isinstance(value[0], str):
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
    if isinstance(value, str):
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
    value = value[0] if isinstance(value, list) and len(value) > 0 else value
    value = None if isinstance(value, list) and len(value) == 0 else value
    return value


def date_to_iso(value: str) -> str:
    value = value.lower()
    value = value.replace("april", "iv")  # The only problemactic month

    value = value.replace("viii", "Aug")
    value = value.replace("iii", "Mar")
    value = value.replace("vii", "July")
    value = value.replace("xii", "Dec")
    value = value.replace("ii", "Feb")
    value = value.replace("iv", "Apr")
    value = value.replace("vi", "June")
    value = value.replace("ix", "Sept")
    value = value.replace("xi", "Nov")
    value = value.replace("i", "Jan")
    value = value.replace("v", "May")
    value = value.replace("x", "Oct")

    try:
        date_ = parser.parse(value).date()
        value = date_.isoformat()[:10]
    except parser.ParserError, IllegalMonthError:
        value = ""

    return value


def remove_trailing_punct(value: str) -> str:
    return re.sub(r"[.,;:]$", "", value)
