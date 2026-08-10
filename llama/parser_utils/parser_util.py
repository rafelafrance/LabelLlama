import re
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from pathlib import Path

FIRST_COLUMNS = ["status", "source", "text", "elapsed"]


def get_front_yaml(text: str, path: Path) -> dict:
    top = re.search("^---$.*^---$", text, flags=re.MULTILINE | re.DOTALL)
    if not top:
        raise ValueError(f"Improperly formatted prompt file. {path}")

    top = top.group(0).replace("---", "")
    front = yaml.safe_load(top)
    return front
