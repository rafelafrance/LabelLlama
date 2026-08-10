import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from llama.parser_utils.field_prompt import FieldPrompt
from llama.parser_utils.prompt_file_parser import PromptFileParser

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class ParserCleaner:
    fields: dict[str, FieldPrompt] = field(default_factory=dict[str, FieldPrompt])
    calc_fields: dict[str, Any] = field(default_factory=dict[str, Any])
    _field_names: list[str] = field(default_factory=list[str])
    _calc_field_names: list[str] = field(default_factory=list[str])
    _field_classes: dict[str, Any] = field(default_factory=dict[str, Any])
    _calc_field_classes: dict[str, Any] = field(default_factory=dict[str, Any])

    @classmethod
    def load(cls, prompt_path: Path) -> ParserCleaner:
        prompt_parser = PromptFileParser.load(prompt_path)
        cleaner = cls(
            fields=prompt_parser.fields,
            calc_fields=prompt_parser.calc_fields,
        )
        return cleaner

    @property
    def field_names(self) -> list[str]:
        if not self._field_names:
            self._field_names = list(self.fields.keys())
        return self._field_names

    @property
    def calc_field_names(self) -> list[str]:
        if not self._calc_field_names:
            self._calc_field_names = list(self.calc_fields.keys())
        return self._calc_field_names

    @property
    def all_field_names(self) -> list[str]:
        return self.field_names + self.calc_field_names

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

    @property
    def all_field_classes(self) -> dict[str, Any]:
        return self.field_classes | self.calc_field_classes

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
