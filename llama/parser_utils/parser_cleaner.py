import re
from dataclasses import dataclass, field
from typing import Any

from llama.parser_utils.field_prompt import FieldPrompt


@dataclass
class ParserCleaner:
    fields: dict[str, FieldPrompt] = field(default_factory=dict[str, FieldPrompt])
    calc_fields: dict[str, Any] = field(default_factory=dict[str, Any])
    _field_classes: dict[str, Any] = field(default_factory=dict[str, Any])
    _calc_field_classes: dict[str, Any] = field(default_factory=dict[str, Any])

    @property
    def field_classes(self) -> dict[str, Any]:
        """Return field classes indexed by column/header name."""
        if not self._field_classes:
            self._field_classes = {
                f.name: f.field_class() for f in self.fields.values()
            }
        return self._field_classes

    @property
    def calc_field_classes(self) -> dict[str, Any]:
        if not self._calc_field_classes:
            self._calc_field_classes = {
                f.name: f.field_class() for f in self.calc_fields.values()
            }
        return self._calc_field_classes

    @staticmethod
    def llm_reply_to_dict(content: str, columns: list[str]) -> dict:
        """Convert an LM reply in llm_prompt.get_field_template format to a dict."""
        # Get field names and the values
        splits = re.split(r"^<< ## (\w+) ##(?: >>)?$", content, flags=re.MULTILINE)

        # Remove first blank split
        if splits[0].strip() == "":
            splits = splits[1:]

        # Try to match field names with values
        as_dict = {
            k: v.strip()
            for k, v in zip(splits[::2], splits[1::2], strict=False)
            if k in columns
        }

        return as_dict
