from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from llama.pylib.prompt_file_parser import PromptFileParser

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class ParserCleaner:
    llm_field_classes: dict[str, Any] = field(default_factory=dict[str, Any])
    calc_field_classes: dict[str, Any] = field(default_factory=dict[str, Any])

    @classmethod
    def load(cls, prompt_path: Path) -> ParserCleaner:
        prompt_parser = PromptFileParser.load(prompt_path)
        cleaner = cls(
            llm_field_classes={
                f.name: f.field_class for f in prompt_parser.fields.values()
            },
            calc_field_classes={
                f.name: f.field_class for f in prompt_parser.calc_fields.values()
            },
        )
        return cleaner
