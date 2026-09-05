"""Fix common problems with values after a language model mangles them."""

import contextlib
import json
import math
import re
from calendar import IllegalMonthError
from dataclasses import dataclass, fields
from datetime import date as dt
from functools import cached_property
from typing import Any

from dateutil import parser
from dateutil.relativedelta import relativedelta

# A minus only counts as a sign when it is not glued to a preceding digit, so a
# range like "12-34" yields [12, 34] rather than [12, -34].
INT = re.compile(r"(?<!\d)-?\d[\d,]*")
# A single optional decimal point; repeated separators like "1.2.3" no longer
# match as one token (and float() is still guarded in str_to_float).
FLOAT = re.compile(r"-?\d+(?:\.\d+)?|\.\d+")

# For parsing dates
SEP = r"[\s(.,/_'-]+"  # Date month, day, year separators
YEAR = r"([12]\d\d\d|\d\d)"
YEAR4 = r"([12]\d\d\d)"
MON_NUM = r"[01]?\d"  # Month as a number

EMPTY: set[str] = {
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

OPEN: tuple[str, ...] = ("(", "[", "{")
CLOSE: tuple[str, ...] = (")", "]", "}")

TITLE_LOWER = {"A", "An", "Of", "The", "De", "And"}

# Months a language model may emit as Roman numerals (plus the long-form
# "april"), mapped to abbreviations that dateutil understands.
ROMAN_MONTHS = {
    "i": "Jan",
    "ii": "Feb",
    "iii": "Mar",
    "iv": "Apr",
    "v": "May",
    "vi": "Jun",
    "vii": "Jul",
    "viii": "Aug",
    "ix": "Sep",
    "x": "Oct",
    "xi": "Nov",
    "xii": "Dec",
    "april": "Apr",
}


@dataclass
class FixParses:
    @cached_property
    def _field_names(self) -> tuple[str, ...]:
        """The dataclass field names, cached so clean_str scans once per instance."""
        return tuple(f.name for f in fields(self))

    @staticmethod
    def _is_bad_float(value: float) -> bool:
        """Return True for NaN/inf floats that should be treated as empty."""
        return math.isnan(value) or math.isinf(value)

    def to_str(self, value: Any) -> str:
        """Coerce any value to a cleaned string (empty string for bad values)."""
        match value:
            case str():
                return self.clean_str(value)
            case float() if self._is_bad_float(value):
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
        """Coerce any value to an int, or None if it cannot be parsed."""
        value = self.list_to_item(value)

        match value:
            case str():
                value = self.clean_str(value)
                return self.str_to_int(value)
            case float() if self._is_bad_float(value):
                return None
            case int() | float() | bool():
                return int(value)
            case _:
                return None

    def to_float(self, value: Any) -> float | None:
        """Coerce any value to a float, or None if it cannot be parsed."""
        value = self.list_to_item(value)

        match value:
            case str():
                value = self.clean_str(value)
                return self.str_to_float(value)
            case float() if self._is_bad_float(value):
                return None
            case int() | float() | bool():
                return float(value)
            case _:
                return None

    def to_bool(self, value: Any) -> bool:
        """Coerce any value to a bool (recognizing true/yes/1/on strings)."""
        value = self.list_to_item(value)

        match value:
            case str():
                value = self.clean_str(value)
                return value.lower() in ("true", "yes", "1", "on")
            case float() if self._is_bad_float(value):
                return False
            case _:
                return bool(value)

    def to_truthy(self, value: Any) -> bool | str:
        """Return True for truthy values, or an empty string for falsy ones."""
        return self.to_bool(value) or ""

    def to_list_of_strs(self, value: Any) -> list[str]:
        """Coerce any value to a list of cleaned strings."""
        value = self.str_to_list(value)

        match value:
            case str():
                value = self.clean_str(value)
                return [value]
            case float() if self._is_bad_float(value):
                return []
            case int() | float() | bool():
                return [str(value)]
            case list() if len(value) > 0:
                return [self.to_str(v) for v in value if v]
            case _:
                return []

    def to_list_of_ints(self, value: Any) -> list[int]:
        """Coerce any value to a list of ints, dropping unparseable items."""
        value = self.str_to_list(value)

        match value:
            case str():
                value = re.sub(r",", "", value)
                return [
                    i
                    for v in INT.findall(value)
                    if (i := self.str_to_int(v)) is not None
                ]
            case float() if self._is_bad_float(value):
                return []
            case int() | float() | bool():
                return [int(value)]
            case list() if len(value) > 0 and isinstance(value[0], str):
                return [c for v in value if (c := self.str_to_int(v))]
            case list() if len(value) > 0:
                return [i for v in value if (i := self.to_int(v))]
            case _:
                return []

    def to_list_of_floats(self, value: Any) -> list[float]:
        """Coerce any value to a list of floats, dropping unparseable items."""
        value = self.str_to_list(value)

        match value:
            case str():
                value = re.sub(r",", "", value)
                return [
                    f
                    for v in FLOAT.findall(value)
                    if (f := self.str_to_float(v)) is not None
                ]
            case float() if self._is_bad_float(value):
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
        """Extract the first float from a string, or None if there is none."""
        m = FLOAT.search(value.replace(",", ""))
        if not m:
            return None
        with contextlib.suppress(ValueError):
            return float(m[0])
        return None

    def str_to_int(self, value: str) -> int | None:
        """Extract the first int from a string, or None if there is none."""
        value = value.replace(",", "")
        m = INT.search(value)
        return int(m[0]) if m else None

    def str_to_list(self, value: Any) -> Any:
        """Parse stringified list ("[1, 2, 3]") into a real list; else pass through."""
        if isinstance(value, str):
            value = self.stringified_list(value)
        return value

    def stringified_list(self, value: str) -> list[Any] | str:
        """json-parse a bracketed string, falling back to the original on error."""
        if value.startswith("[") and value.endswith("]"):
            if value[1] == "'":
                value = value.replace('"', r"\"")
                value = value.replace("'", '"')

            with contextlib.suppress(json.decoder.JSONDecodeError):
                value = json.loads(value)

        return value

    def clean_str(self, value: str) -> str:
        """Strip whitespace, empty-field notations, brackets, quotes, and markdown."""
        value = value.strip()

        # Notations for an empty field
        if value.lower() in EMPTY:
            return ""

        # Notations for an empty string involving a field name
        if any(
            value == pat.format(name)
            for name in self._field_names
            for pat in EMPTY_FIELD
        ):
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
        """Reduce a list to its first item (or None for an empty list)."""
        value = value[0] if isinstance(value, list) and len(value) > 0 else value
        value = None if isinstance(value, list) and len(value) == 0 else value
        return value

    def date_to_iso(self, value: str) -> str:
        """Normalize a messy date string to ISO (YYYY-MM-DD or YYYY-MM)."""
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

        # Map any Roman-numeral month (and "april") to a name dateutil parses.
        # Only the month tokens change; other letters/digits are left untouched.
        value = " ".join(
            ROMAN_MONTHS.get(token, token) for token in re.split(SEP, value) if token
        )

        try:
            date_ = parser.parse(value).date()

            # A bare date that lands in the future is assumed to be roughly a
            # century old (common for historical specimens), so shift it back.
            if date_ > dt.today():
                date_ -= relativedelta(years=100)

            end = 7 if short_date else 10
            value = date_.isoformat()[:end]

        except parser.ParserError, IllegalMonthError:
            value = ""

        return value

    def remove_leading_punct(self, value: str) -> str:
        """Strip leading whitespace and punctuation."""
        return re.sub(r"^[\s\"'.,;:(){}\[\]\-]+", "", value)

    def remove_trailing_punct(self, value: str) -> str:
        """Strip trailing whitespace and punctuation."""
        return re.sub(r"[\s\"'.,;:(){}\[\]\-]+$", "", value)

    def clean_str_ends(self, value: str) -> str:
        """Strip leading and trailing whitespace and punctuation."""
        value = self.remove_leading_punct(value)
        value = self.remove_trailing_punct(value)
        return value

    def reduce_list(self, value: list[Any]) -> Any | None:
        """Collapse a list to its single item, or return it unchanged."""
        if not value:
            return []
        if len(value) == 1:
            return value[0]
        return value

    def reduce_str_list(self, value: list[str] | str) -> str:
        """Collapse a single-item list to its string, or join a multi-item list."""
        if isinstance(value, str):
            return value
        if not value:
            return ""
        if len(value) == 1:
            return value[0]
        return ", ".join(value)

    def hallucinated_str(self, value: str, text: str) -> str:
        """Return value only if it appears (case-insensitively) in text; else ''."""
        value = self.to_str(value)
        if not text:
            return value
        pattern = re.escape(str(value))
        value = value if re.search(pattern, text, flags=re.IGNORECASE) else ""
        return value

    @staticmethod
    def title_with_exceptions(value: str) -> str:
        """Title-case a string but keep small words (a, of, the, ...) lowercase."""
        words = value.title().split()
        words = [
            w.lower() if (i and w in TITLE_LOWER) else w for i, w in enumerate(words)
        ]
        return " ".join(words)
