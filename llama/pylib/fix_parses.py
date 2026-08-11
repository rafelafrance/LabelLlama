"""Fix common problems with values after a language model mangles them."""

import contextlib
import json
import math
import re
from calendar import IllegalMonthError
from dataclasses import dataclass, fields
from datetime import date as dt
from typing import Any

from dateutil import parser
from dateutil.relativedelta import relativedelta

INT = re.compile(r"[-]?[\d,]+")
FLOAT = re.compile(r" [-]? \d+ [\d,.]* | \.\d+", flags=re.VERBOSE)

# For parsing dates
SEP = r"[\s(.,/_'-]+"  # Date month, day, year separators
YEAR = r"([12]\d\d\d|\d\d)"
YEAR4 = r"([12]\d\d\d)"
MON_NUM = r"[01]?\d"  # Month as a number

EMPTY: set = {
    "''",
    "[",
    "]",
    "[]",
    "—",
    '""',
    '{""}',
    "nan",
    "blank",
    "(blank)",
    "[blank]",
    "{blank}",
    "empty",
    "(empty)",
    "[empty]",
    "{empty}",
    "none",
    "(none)",
    "[none]",
    "{none}",
    "not present",
    "(not present)",
    "[not present]",
    "{not present}",
    "not specified",
    "(not specified)",
    "[not specified]",
    "{not specified}",
}
EMPTY_FIELD = [
    "{0}",
    "({0})",
    "[{0}]",
    "{{{0}}}",
]

OPEN: tuple = ("(", "[", "{")
CLOSE: tuple = (")", "]", "}")

TITLE_LOWER = {"A", "An", "Of", "The", "De", "And"}


@dataclass
class FixParses:
    def to_str(self, value: Any) -> str:
        match value:
            case str():
                return self.clean_str(value)
            case float() if math.isnan(value) or math.isinf(value):
                return ""
            case int() | float() | bool():
                return str(value)
            case list() if len(value) > 0 and isinstance(value[0], str):
                return " ".join(c for v in value if (c := self.clean_str(v)))
            case list():
                return " ".join(str(v) for v in value)
            case _:
                return ""

    def to_int(self, value: Any) -> int | None:
        value = self.list_to_item(value)

        match value:
            case str():
                value = self.clean_str(value)
                return self.str_to_int(value)
            case float() if math.isnan(value) or math.isinf(value):
                return None
            case int() | float() | bool():
                return int(value)
            case _:
                return None

    def to_float(self, value: Any) -> float | None:
        value = self.list_to_item(value)

        match value:
            case str():
                value = self.clean_str(value)
                return self.str_to_float(value)
            case float() if math.isnan(value) or math.isinf(value):
                return None
            case int() | float() | bool():
                return float(value)
            case _:
                return None

    def to_bool(self, value: Any) -> bool:
        value = self.list_to_item(value)

        match value:
            case str():
                value = self.clean_str(value)
                return value.lower() in ("true", "yes", "1", "on")
            case float() if math.isnan(value) or math.isinf(value):
                return False
            case _:
                return bool(value)

    def to_truthy(self, value: Any) -> bool | str:
        return self.to_bool(value) or ""

    def to_list_of_strs(self, value: Any) -> list[str]:
        value = self.str_to_list(value)

        match value:
            case str():
                value = self.clean_str(value)
                return [value]
            case float() if math.isnan(value) or math.isinf(value):
                return []
            case int() | float() | bool():
                return [str(value)]
            case list() if len(value) > 0:
                return [self.to_str(v) for v in value if v]
            case _:
                return []

    def to_list_of_ints(self, value: Any) -> list[int]:
        value = self.str_to_list(value)

        match value:
            case str():
                value = re.sub(r",", "", value)
                return [
                    i
                    for v in INT.findall(value)
                    if (i := self.str_to_int(v)) is not None
                ]
            case float() if math.isnan(value) or math.isinf(value):
                return []
            case int() | float() | bool():
                return [int(value)]
            case list() if len(value) > 1 and isinstance(value[0], str):
                return [c for v in value if (c := self.str_to_int(v))]
            case list() if len(value) > 0:
                return [i for v in value if (i := self.to_int(v))]
            case _:
                return []

    def to_list_of_floats(self, value: Any) -> list[float]:
        value = self.str_to_list(value)

        match value:
            case str():
                value = re.sub(r",", "", value)
                return [
                    f
                    for v in FLOAT.findall(value)
                    if (f := self.str_to_float(v)) is not None
                ]
            case float() if math.isnan(value) or math.isinf(value):
                return []
            case int() | float() | bool():
                return [float(value)]
            case list() if len(value) > 0 and isinstance(value[0], str):
                return [f for v in value if (f := self.str_to_float(v))]
            case list():
                return [f for v in value if (f := self.to_float(v))]
            case _:
                return []

    def str_to_float(self, value: str) -> float | None:
        value = value.replace(",", "")
        m = FLOAT.search(value)
        return float(m[0]) if m else None

    def str_to_int(self, value: str) -> int | None:
        value = value.replace(",", "")
        m = INT.search(value)
        return int(m[0]) if m else None

    def str_to_list(self, value: Any) -> list[Any] | Any:
        if isinstance(value, str):
            value = self.stringified_list(value)
        return value

    def stringified_list(self, value: str) -> list[Any] | str:
        if value.startswith("[") and value.endswith("]"):
            if value[1] == "'":
                value = value.replace('"', r"\"")
                value = value.replace("'", '"')

            with contextlib.suppress(json.decoder.JSONDecodeError):
                value = json.loads(value)

        return value

    def clean_str(self, value: str) -> str:
        value = value.strip()

        # Notations for an empty field
        if value.lower() in EMPTY:
            return ""

        # Notations for an empty string involving a field name
        for field in [f.name for f in fields(self)]:
            if any(value == pat.format(field) for pat in EMPTY_FIELD):
                return ""

        # Remove surrounding brackets
        if len(value) > 0 and value[0] in OPEN and value[-1] in CLOSE:
            value = value[1:-1]

        # Remove leading and trailing quotes
        value = re.sub(r'^"(.+)"$', r"\1", value)
        value = re.sub(r"^'(.+)'$", r"\1", value)

        # Remove bold and italic ( "**text**" and "_text_") markdown notations
        value = re.sub(r"([*_]+)([\w\s]*)\1", r"\2", value)

        return value

    def list_to_item(self, value: Any) -> Any:
        value = value[0] if isinstance(value, list) and len(value) > 0 else value
        value = None if isinstance(value, list) and len(value) == 0 else value
        return value

    def date_to_iso(self, value: str) -> str:
        value = value.lower().strip()

        short_date = re.match(
            rf""" ^ (?:
                [a-z]+    {SEP} {YEAR}
                | {YEAR}    {SEP} [a-z]+
                | {MON_NUM} {SEP} {YEAR4}
                ) [.,;:_-]* $ """,
            value,
            flags=re.IGNORECASE | re.VERBOSE,
        )

        bad_short_date = re.match(
            rf""" ^ \d+ {SEP} \d+ $ """, value, flags=re.IGNORECASE | re.VERBOSE
        )
        if not short_date and bad_short_date:
            return ""

        value = value.replace("april", "iv")  # The only month w/ roman numerals in it

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

            if date_ > dt.today():
                date_ -= relativedelta(years=100)

            end = 7 if short_date else 10
            value = date_.isoformat()[:end]

        except parser.ParserError, IllegalMonthError:
            value = ""

        return value

    def remove_leading_punct(self, value: str) -> str:
        return re.sub(r"^[\s\"'.,;:(){}\[\]\-]+", "", value)

    def remove_trailing_punct(self, value: str) -> str:
        return re.sub(r"[\s\"'.,;:(){}\[\]\-]+$", "", value)

    def clean_str_ends(self, value: str) -> str:
        value = self.remove_leading_punct(value)
        value = self.remove_trailing_punct(value)
        return value

    def reduce_list(self, value: list[Any]) -> Any | None:
        if not value:
            return []
        if len(value) == 1:
            return value[0]
        return value

    def reduce_str_list(self, value: list[str] | str) -> str:
        if not value:
            return ""
        if len(value) == 1:
            return value[0]
        return str(value)

    def hallucinated_str(self, value: str, text: str) -> str:
        value = self.to_str(value)
        if not text:
            return value
        pattern = re.escape(str(value))
        value = value if re.search(pattern, text, flags=re.IGNORECASE) else ""
        return value

    @staticmethod
    def title_with_exceptions(value: str) -> str:
        words = value.title().split()
        words = [
            w.lower() if (i and w in TITLE_LOWER) else w for i, w in enumerate(words)
        ]
        return " ".join(words)
