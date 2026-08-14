import importlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from llama.pylib.prompt_util import get_front_yaml

FIELD_PROMPT_DIR = Path("prompts")


@dataclass
class FieldPrompt:
    name: str
    description: str
    module: Path
    columns: list[str] = field(default_factory=list[str])
    prompts: list[str] = field(default_factory=list[str])
    field_class: Any = None

    @classmethod
    def load(cls, link: str) -> FieldPrompt:
        path = FIELD_PROMPT_DIR / link
        with path.open() as f:
            text = f.read()

        front = get_front_yaml(text, path)

        sections = re.split(r"^(?<!#)#\sPrompt\s+(\w+)$", text, flags=re.MULTILINE)
        columns, prompts = [], []
        for column, prompt in zip(sections[1::2], sections[2::2], strict=True):
            columns.append(column.strip())
            prompts.append(prompt.strip())

        field_prompt = cls(
            name=front["name"],
            description=front["description"],
            module=Path(front["module"]),
            columns=columns,
            prompts=prompts,
        )
        field_prompt.field_class = field_prompt._field_class()

        return field_prompt

    def _field_class(self) -> Any:
        cls_name = self.name[0].upper() + self.name[1:]
        mod_name = str(self.module).removesuffix(".py").replace("/", ".")
        module = importlib.import_module(mod_name)
        cls = getattr(module, cls_name)
        return cls
