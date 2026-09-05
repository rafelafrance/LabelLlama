"""Consistency checks for the prompt markdown files in prompts/."""

from pathlib import Path

import pytest

from llama.model_utils.prompt_file_parser import FIELD_PROMPT_DIR, PromptFileParser


PROMPT_FILES = sorted(FIELD_PROMPT_DIR.glob("*.md"))


def test_prompt_files_exist() -> None:
    assert PROMPT_FILES, f"No prompt files found in {FIELD_PROMPT_DIR}"


@pytest.mark.parametrize(
    "prompt_path",
    PROMPT_FILES,
    ids=[p.name for p in PROMPT_FILES],
)
def test_required_fields_are_llm_fields(prompt_path: Path) -> None:
    """Every name in the (optional) Required Fields section must be an LLM Field."""
    parser = PromptFileParser.load(prompt_path)
    if not parser.req_fields:
        pytest.skip(f"{prompt_path.name} has no Required Fields section")

    llm_field_names = {fld.name for fld in parser.llm_fields}
    missing = [name for name in parser.req_fields if name not in llm_field_names]
    assert not missing, (
        f"{prompt_path.name}: required fields missing from LLM Fields: "
        f"{', '.join(missing)}"
    )
