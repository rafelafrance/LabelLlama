import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CalcField:
    module: Path
    columns: list[str] = field(default_factory=list[str])
    field_class: Any = None

    @classmethod
    def load(cls, link: str) -> CalcField:
        lnk = Path(link)
        cls_name = lnk.stem
        mod_name = link.removeprefix("../").removesuffix(".py").replace("/", ".")
        module = importlib.import_module(mod_name)
        field_class = getattr(module, cls_name)

        calc_field = cls(
            module=lnk,
            columns=field_class().get_field_names(),
            field_class=getattr(module, cls_name),
        )
        return calc_field
