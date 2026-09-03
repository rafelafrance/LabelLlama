from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from llama.prompt_utils.prompt_file_parser import PromptFileParser

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class ParserCleaner:
    llm_field_classes: dict[str, Any] = field(default_factory=dict)
    calc_field_classes: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, prompt_path: Path) -> ParserCleaner:
        prompt_parser = PromptFileParser.load(prompt_path)
        cleaner = cls(
            llm_field_classes={f.name: f.field_class for f in prompt_parser.llm_fields},
            calc_field_classes={
                f.name: f.field_class for f in prompt_parser.calc_fields
            },
        )
        return cleaner
