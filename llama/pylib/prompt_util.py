import importlib
import re
from pathlib import Path
from typing import Any

FIELD_MODULE_DIR = Path(__file__).parent.parent / "fields"
FIEL_MODULE_EXCLUDE = ("__pycache__",)

FIELD_PROMPT_DIR = Path("prompts") / "fields"
FIELD_PROMPT_EXCLUDE = ("refine",)

LM_PROMPT_DIRS = [Path("prompts") / "fields", Path("prompts") / "fields" / "refine"]

MIN_PROMPT_LEN = 40


# ---------------------------------------------------------------------
def normalize(path: Path) -> str:
    norm = re.sub(r"^.*?fields/", "", str(path))
    norm = re.sub(r"\.py|\.md", "", norm)
    return norm


def to_class_name(path: Path) -> str:
    """Convert a field name into its class name."""
    name = path.stem
    cls_name = name[0].upper() + name[1:]
    return cls_name


def to_prompt_path(field_name: str) -> Path:
    prompt_path = f"{FIELD_PROMPT_DIR}/{field_name}.md"
    return Path(prompt_path)


# ---------------------------------------------------------------------
def get_field_modules() -> list[Path]:
    """Get all the field modules paths."""
    dirs = [
        d for d in FIELD_MODULE_DIR.iterdir()
        if d.is_dir() and d.stem not in FIEL_MODULE_EXCLUDE
    ]
    files = []
    for d in dirs:
        files += [f for f in sorted(d.glob("*.py")) if f.is_file() and f.stem[0] != "_"]
    return files


def get_field_prompts() ->list[Path]:
    """Get all the fields parsing file paths."""
    dirs = [
        d for d in FIELD_PROMPT_DIR.iterdir()
        if d.is_dir() and d.stem not in FIELD_PROMPT_EXCLUDE
    ]
    files = []
    for d in dirs:
        files += [f for f in sorted(d.glob("*.md")) if f.is_file()]
    return files


def get_lm_prompts() -> list[Path]:
    """Get LM information extraction prompt file paths."""
    files = []
    for d in LM_PROMPT_DIRS:
        files += [f for f in sorted(d.glob("*.md")) if f.is_file()]
    return files


def get_field_classes() -> list:
    """Get all the field classes in the fields files."""
    field_modules = get_field_modules()
    classes = []
    for path in field_modules:
        cls_name = to_class_name(path)
        mod_name = re.sub(r"^.*?LabelLlama/", "", str(path))
        mod_name = mod_name.removesuffix(".py")
        mod_name = mod_name.replace("/", ".")
        module = importlib.import_module(mod_name)
        classes.append(getattr(module, cls_name))
    return classes


# ---------------------------------------------------------------------
def field_modules_by_name() -> dict[str, Path]:
    return {normalize(m): m for m in get_field_modules()}


def field_prompts_by_name() -> dict[str, Path]:
    return {normalize(m): m for m in get_field_prompts()}


def field_classes_by_name() -> dict[str, Any]:
    return {cls.__name__: cls for cls in get_field_classes()}

# ---------------------------------------------------------------------
def build_text_prompt(text: str) -> str:
    return "Extract data from this `text` (str):\n" + text


def build_field_prompts(field_names: list[str]) -> str:
    """Get prompts of all fields given in the field list."""
    prompts = []
    for i, field_name in enumerate(field_names, 1):
        prompt_path = to_prompt_path(field_name)
        with prompt_path.open() as f:
            prompt = f.read()
        prompts.append(f"{i}. {prompt}")
    return "\n\n".join(prompts)


def build_field_template(field_names: list[str]) -> str:
    """Provide a structure for GPT output to workaround GPT's poor JSON formatting."""
    fields = [f.split("/")[-1] for f in field_names]
    template = ["Structure all output with the following template."]
    template += [f"<< ## {f} ## >>\n{{{f}}}" for f in fields]
    template.append("<< ## completed ## >>")
    return "\n\n".join(template)


# ---------------------------------------------------------------------
# The system prompt section
SYS_PROMPT = re.compile(r"^System\s+Prompt", flags=re.IGNORECASE)

# The output fields section
OUT_FIELDS = re.compile(r"^Output\s+Fields", flags=re.IGNORECASE)


def read_lm_prompt(path: Path) -> tuple[str, list[str]]:
    """Read a Markdown prompt file & return the system prompt and field name list."""
    sys_prompt: str = ""
    field_names: list[str] = []

    with path.open() as f:
        raw = f.read()

    # Split Markdown file into sections using headers
    sections = re.split(r"^(?<!#)#\s", raw, flags=re.MULTILINE)

    for section in sections:
        section = section.strip()

        # Get system prompt section
        if SYS_PROMPT.match(section):
            sys_prompt = SYS_PROMPT.sub("", section).strip()

        # Get output fields list section
        elif OUT_FIELDS.match(section):
            section = OUT_FIELDS.sub("", section).strip()
            links = re.findall(r"\([\w/]+\.md\)", section)
            field_names = [lk.removeprefix("(").removesuffix(".md)") for lk in links]

    return sys_prompt, field_names


def read_prompt(path: Path) -> str:
    sys_prompt, _ = read_lm_prompt(path)
    return sys_prompt
