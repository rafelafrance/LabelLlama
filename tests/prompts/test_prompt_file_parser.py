"""
Hardening tests for PromptFileParser.

- Front matter ends at the NEXT '---' line, not the last one in the file.
- Only known section headings split the document; a single '# ' line inside
  a section body must not truncate that section.
- Field links are markdown links; bare parentheses in prose are not links.
- FIELD_PROMPT_DIR is absolute (cwd independent).
"""

from typing import TYPE_CHECKING

from llama.prompts.prompt_file_parser import (
    FIELD_PROMPT_DIR,
    PromptFileParser,
    get_front_yaml,
)

if TYPE_CHECKING:
    from pathlib import Path

FAMILY_LINK = "- [family](../llama/llm_fields/taxon/family.py)"


def write_prompt(tmp_path: Path, body: str, name: str = "test_prompt") -> Path:
    path = tmp_path / f"{name}.md"
    text = f"---\nname: {name}\ndescription: A test prompt.\n---\n\n{body}"
    path.write_text(text, encoding="utf-8")
    return path


def test_front_yaml_stops_at_first_closing_rule(tmp_path: Path) -> None:
    body = (
        "# System Message\n\n"
        "Do the thing.\n\n"
        "---\n\n"
        "A horizontal rule later in the file.\n"
    )
    path = write_prompt(tmp_path, body)
    front = get_front_yaml(path.read_text(encoding="utf-8"), path)
    assert front == {"name": "test_prompt", "description": "A test prompt."}


def test_heading_in_body_does_not_truncate_section(tmp_path: Path) -> None:
    body = (
        "# System Message\n\n"
        "First paragraph.\n\n"
        "# A heading inside the body\n\n"
        "Second paragraph.\n\n"
        "# LLM Fields\n\n"
        f"{FAMILY_LINK}\n"
    )
    path = write_prompt(tmp_path, body)
    parser = PromptFileParser.load(path)

    assert "First paragraph." in parser.system_msg
    assert "A heading inside the body" in parser.system_msg
    assert "Second paragraph." in parser.system_msg
    assert [f.name for f in parser.llm_fields] == ["family"]


def test_field_links_ignore_stray_parentheses(tmp_path: Path) -> None:
    body = (
        "# LLM Fields\n\n"
        f"{FAMILY_LINK}\n"
        "Note (v2): bare parentheses in the prose are not links.\n"
    )
    path = write_prompt(tmp_path, body)
    parser = PromptFileParser.load(path)

    assert [f.name for f in parser.llm_fields] == ["family"]


def test_field_prompt_dir_is_absolute() -> None:
    assert FIELD_PROMPT_DIR.is_absolute()
    assert (FIELD_PROMPT_DIR / "herbarium_v2.md").is_file()


def test_herbarium_v2_sections_stable() -> None:
    """
    Pin the real prompt: the section/link regex changes must not drop
    any fields.
    """
    parser = PromptFileParser.load(FIELD_PROMPT_DIR / "herbarium_v2.md")

    assert parser.name == "herbarium_v2"
    assert len(parser.llm_fields) == 40
    assert len(parser.calc_fields) == 9
    assert parser.req_fields == ["scientificName"]
