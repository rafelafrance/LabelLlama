import importlib.util as iu
import logging
import re
from pathlib import Path

from llama.pylib.str_util import snake_to_camel

FIELD_DIR = Path(__file__).parent.parent / "fields"
print(FIELD_DIR)
EXCLUDE = ("__pycache__",)

MIN_PROMPT_LEN = 40


def get_field_dirs() -> list[Path]:
    return [d for d in FIELD_DIR.iterdir() if d.is_dir() and d.stem not in EXCLUDE]


def get_field_files(dir_: Path) -> list[Path]:
    return [f for f in sorted(dir_.glob("*.py")) if f.is_file() and f.stem[0] != "_"]


def get_all_field_files() -> list[Path]:
    dirs = get_field_dirs()
    files = []
    for d in dirs:
        files += get_field_files(d)
    return files


def prompt_file_ok(path: Path) -> bool:
    ok = True
    prompt, field_list = read_field_list_prompts(path)
    if not prompt:
        logging.error(f"{path.name} is missing a prompt section.")
        ok = False
    elif len(prompt) < MIN_PROMPT_LEN:
        logging.warning("The prompt seems awfully short.")
        ok = False

    if field_list:
        ok &= field_list_ok(path)
    else:
        logging.info("There are no fields in this prompt file.")

    return ok

def field_list_ok(path: Path) -> bool:
    _, field_list = read_field_list_prompts(path)
    names = {snake_to_camel(f.stem): f for f in get_all_field_files()}
    ok = True
    for field in field_list:
        if field not in names:
            ok = False
            logging.error(f"{field} is not available as field to extract.")
    return ok


def get_field_prompts(fields: list[str]) -> str:
    """
    Get prompts of all fields given in the field list.

    Dynamically load the appropriate modules that contain the prompts.
    The module names are in snake case and the target fields are in camel case.
    """
    names = {snake_to_camel(f.stem): f for f in get_all_field_files()}
    prompts = []
    for field in fields:
        path = names[field]
        spec = iu.spec_from_file_location(path.stem, path)
        if spec is None:
            raise ValueError
        module = iu.module_from_spec(spec)
        if module is None or spec.loader is None:
            raise ValueError
        spec.loader.exec_module(module)
        prompts.append(getattr(module, module.__name__.upper()))
    return "\n\n".join(prompts)


def get_text_prompt(text: str) -> str:
    return "Extract data from this `text` (str):\n" + text


def read_field_list_prompts(path: Path) -> tuple[str, list[str]]:
    prompt: str = ""
    fields: list[str] = []
    with path.open() as f:
        raw = f.read()
    parts = re.split(r"^(?<!#)#\s", raw, flags=re.MULTILINE)
    for part in parts:
        part = part.strip()
        if part.startswith("Prompt"):
            prompt = part.replace("Prompt", "").strip()
        elif part.startswith("Fields"):
            part = part.replace("Fields", "").strip()
            part = part.replace("-", "")
            fields = part.split()
    return prompt, fields


def read_prompt(path: Path) -> str:
    prompt, _ = read_field_list_prompts(path)
    return prompt
