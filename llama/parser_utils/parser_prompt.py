from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from llama.parser_utils.field_prompt import FieldPrompt
from llama.pylib.prompt_file_parser import PromptFileParser

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class ParserPrompt:
    # -------------- ClassVars ---------------
    text_msg: ClassVar[str] = """Extract data from this `text` (str):\n\n"""
    # ----------------------------------------

    name: str = ""
    description: str = ""
    system_msg: str = ""
    fields: dict[str, FieldPrompt] = field(default_factory=dict[str, FieldPrompt])
    field_prompts: str = ""
    field_template: str = ""
    _user_msg: str = ""
    _columns: list[str] = field(default_factory=list[str])

    @classmethod
    def load(cls, prompt_path: Path) -> ParserPrompt:
        prompt_parser = PromptFileParser.load(prompt_path)
        prompt = cls(
            name=prompt_parser.name,
            description=prompt_parser.description,
            system_msg=prompt_parser.system_msg,
            fields=prompt_parser.fields,
        )
        if prompt.fields:
            prompt.field_prompts = prompt.build_field_prompts()
            prompt.field_template = prompt.build_field_template()

        return prompt

    @property
    def user_msg(self) -> str:
        if not self._user_msg:
            self._user_msg = "\n\n".join(
                [p for p in (self.field_prompts, self.field_template) if p]
            )
        return self._user_msg

    @property
    def column_names(self) -> list[str]:
        """Get all column names."""
        if not self._columns:
            for field_ in self.fields.values():
                self._columns += field_.columns
        return self._columns

    def build_field_prompts(self) -> str:
        formatted = [
            f"{i}. {p}"
            for f in self.fields.values()
            for i, p in enumerate(f.prompts, 1)
        ]
        self.field_prompts = "\n".join(formatted)
        return self.field_prompts

    def build_field_template(self) -> str:
        template = ["Structure all output with the following template."]
        template += [
            f"<< ## {c} ## >>\n{{{c}}}" for f in self.fields.values() for c in f.columns
        ]
        template.append("<< ## completed ## >>")
        self.field_template = "\n\n".join(template)
        return self.field_template

    def build_text_msg(self, text: str) -> str:
        return self.text_msg + text
