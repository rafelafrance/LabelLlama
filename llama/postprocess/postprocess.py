from typing import Any


def clean_empties(struct: dict[str, Any]) -> None:
    for key, value in struct.items():
        struct[key] = "" if value == "[]" else value
        struct[key] = "" if value == '""' else value
