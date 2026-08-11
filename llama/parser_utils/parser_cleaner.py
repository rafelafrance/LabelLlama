import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from llama.parser_utils.prompt_file_parser import PromptFileParser

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class ParserCleaner:
    field_classes: dict[str, Any] = field(default_factory=dict[str, Any])
    calc_field_classes: dict[str, Any] = field(default_factory=dict[str, Any])

    @classmethod
    def load(cls, prompt_path: Path) -> ParserCleaner:
        prompt_parser = PromptFileParser.load(prompt_path)
        cleaner = cls(
            field_classes={
                f.name: f.field_class for f in prompt_parser.fields.values()
            },
            calc_field_classes={
                f.name: f.field_class for f in prompt_parser.calc_fields.values()
            },
        )
        return cleaner

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
