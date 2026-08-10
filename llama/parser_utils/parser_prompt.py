import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from llama.parser_utils.field_prompt import FieldPrompt
from llama.parser_utils.prompt_file_parser import PromptFileParser

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class ParserPrompt:
    # -------------- ClassVars ---------------
    text_prompt: ClassVar[str] = "Extract data from this `text` (str):\n"
    # ----------------------------------------

    name: str
    description: str
    base_prompt: str = ""
    fields: dict[str, FieldPrompt] = field(default_factory=dict[str, FieldPrompt])
    field_prompts: str = ""
    field_template: str = ""
    _system_prompt: str = ""
    _columns: list[str] = field(default_factory=list[str])

    @classmethod
    def load(cls, prompt_path: Path) -> ParserPrompt:
        prompt_parser = PromptFileParser.load(prompt_path)
        prompt = cls(
            name=prompt_parser.name,
            description=prompt_parser.description,
            base_prompt=prompt_parser.base_prompt,
            fields=prompt_parser.fields,
        )
        if prompt.fields:
            prompt.field_prompts = prompt.build_field_prompts()
            prompt.field_template = prompt.build_field_template()

        return prompt

    @property
    def system_prompt(self) -> str:
        if not self._system_prompt:
            self._system_prompt = "\n\n".join(
                [
                    p
                    for p in (self.base_prompt, self.field_prompts, self.field_template)
                    if p
                ]
            )
        return self._system_prompt

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

    def log_size(self) -> None:
        sys_prompt = self.system_prompt
        length = len(sys_prompt)
        words = len(sys_prompt.split())
        logging.info(
            f"Prompt lengths (without payload) = {length} characters, {words} words"
        )

    def build_text_prompt(self, text: str) -> str:
        return self.text_prompt + text
