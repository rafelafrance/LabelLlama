import importlib.util as iu
from pathlib import Path

from llama.pylib.str_util import snake_to_camel

FIELD_DIR = Path(__file__).parent


def get_field_dirs() -> list[Path]:
    return [d for d in FIELD_DIR.iterdir() if d.is_dir()]


def get_field_files(dir_: Path) -> list[Path]:
    return [f for f in dir_.iterdir() if f.is_file()]


def get_all_field_files() -> list[Path]:
    dirs = get_field_dirs()
    files = []
    for d in dirs:
        files += get_field_files(d)
    return files


def get_prompts(fields: list[str]) -> list[str]:
    """
    Get prompts of all fields given in the field list.

    The fields are in camel case.
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

    for p in prompts:
        print(p)
        print()
    return prompts
