import importlib
import importlib.util as iu
import logging
import re
from pathlib import Path
from typing import Any

from llama.pylib.str_util import snake_to_camel

FIELD_DIR = Path(__file__).parent.parent / "fields"
EXCLUDE = ("__pycache__",)

MIN_PROMPT_LEN = 40


def get_field_dirs() -> list[Path]:
    """Get all the directories with field parsing scripts in them."""
    return [d for d in FIELD_DIR.iterdir() if d.is_dir() and d.stem not in EXCLUDE]


def get_field_files(dir_: Path) -> list[Path]:
    """Get all the field parsing file names in a directory."""
    return [f for f in sorted(dir_.glob("*.py")) if f.is_file() and f.stem[0] != "_"]


def get_all_field_files() -> list[Path]:
    """Get all the fields parsing file paths."""
    dirs = get_field_dirs()
    files = []
    for d in dirs:
        files += get_field_files(d)
    return files


def get_field_classes(field_list: list[str]) -> dict[str, Any]:
    """Get all the field classes in the fields files."""
    names = get_field_files_by_name()
    classes = {}
    for field in field_list:
        if field in names:
            cls_name = field[0].upper() + field[1:]
            mod_name = re.sub(r".*?LabelLlama/", "", str(names[field]))
            mod_name = mod_name.removesuffix(".py")
            mod_name = mod_name.replace("/", ".")
            module = importlib.import_module(mod_name)
            classes[field] = getattr(module, cls_name)
    return classes


def get_field_files_by_name() -> dict[str, Path]:
    return {snake_to_camel(f.stem): f for f in get_all_field_files()}


def prompt_file_ok(path: Path) -> bool:
    """Check if the Markdown prompt file parses OK."""
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
    """Look for invalid field characters in the field list."""
    _, field_list = read_field_list_prompts(path)
    names = get_field_files_by_name()
    ok = True
    for field in field_list:
        if field not in names:
            ok = False
            logging.error(f"{field} is not available as field to extract.")
    return ok


def get_field_template(fields: list[str]) -> str:
    """Workaround GPT's terrible JSON formatting."""
    template = ["Structured all output with the following template."]
    template += [f"<< ## {f} ## >>\n{{{f}}}" for f in fields]
    template.append("<< ## completed ## >>")
    return "\n\n".join(template)


def get_field_prompts(fields: list[str]) -> str:
    """
    Get prompts of all fields given in the field list.

    Dynamically load the appropriate modules that contain the prompts.
    The module names are in snake case and the target fields are in camel case.
    """
    names = get_field_files_by_name()
    prompts = []
    for i, field in enumerate(fields, 1):
        path = names[field]
        spec = iu.spec_from_file_location(path.stem, path)
        if spec is None:
            raise ValueError
        module = iu.module_from_spec(spec)
        if module is None or spec.loader is None:
            raise ValueError
        spec.loader.exec_module(module)
        prompt = getattr(module, module.__name__.upper())
        prompts.append(f"{i}. {prompt}")
    return "\n\n".join(prompts)


def get_text_prompt(text: str) -> str:
    return "Extract data from this `text` (str):\n" + text


def read_prompt(path: Path) -> str:
    prompt, _ = read_field_list_prompts(path)
    return prompt


# ---------------------------------------------------------------------
# Split Markdown file into sections using headers
SECTIONS = re.compile(r"^(?<!#)#\s", flags=re.MULTILINE)

# The system prompt section
SYS_PROMPT = re.compile(r"^System\s+Prompt", flags=re.IGNORECASE)

# The output fields section
OUT_FIELDS = re.compile(r"^Output\s+Fields", flags=re.IGNORECASE)


def read_field_list_prompts(path: Path) -> tuple[str, list[str]]:
    """Read a Markdown prompt file & return the system prompt and output fields list."""
    prompt: str = ""
    fields: list[str] = []

    with path.open() as f:
        raw = f.read()

    # Split Markdown file into sections using headers
    sections = SECTIONS.split(raw)

    for section in sections:
        section = section.strip()

        # Get system prompt section
        if SYS_PROMPT.search(section):
            prompt = SYS_PROMPT.sub("", prompt).strip()

        # Get output fields list section
        elif OUT_FIELDS.search(section):
            section = OUT_FIELDS.sub("", section).strip()
            section = section.replace("-", "")  # Remove Markdown list characters
            fields = section.split()

    return prompt, fields
