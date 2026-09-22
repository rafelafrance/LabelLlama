import logging
from typing import TYPE_CHECKING

from llama.results.parsed_docs import ParsedDocs

if TYPE_CHECKING:
    from pathlib import Path

    from llama.prompts.prompt import Prompt

REQUIRED_CLEANER_COLUMNS = {"status", "source", "text"}


class FieldCleaner:
    def __init__(
        self, prompt: Prompt, parsed_file: Path, limit: int | None = None
    ) -> None:
        self.columns = prompt.columns
        self.llm_field_classes = {f.name: f.field_class for f in prompt.llm_fields}
        self.calc_field_classes = {f.name: f.field_class for f in prompt.calc_fields}

        self.parsed_docs, _ = ParsedDocs.read_parsed_docs(
            parsed_file, prompt.columns, strict_columns=False
        )

        if not self.parsed_docs:
            raise ValueError(f"{parsed_file} has no successful docs to clean")

        self.parsed_docs = self.parsed_docs[:limit]

        parsed_columns = list(self.parsed_docs[0].keys())
        self.validate_columns(parsed_columns)

        self.llm_columns = [c for c in self.columns if c in self.llm_field_classes]
        self.calc_columns = list(self.calc_field_classes)
        self.output_columns = self.get_output_columns()

        logging.info(f"Read {len(self.parsed_docs)} row(s) from {parsed_file}")

    def validate_columns(self, parsed_columns: list[str]) -> None:
        missing_required = REQUIRED_CLEANER_COLUMNS - set(parsed_columns)
        if missing_required:
            missing = ", ".join(sorted(missing_required))
            raise ValueError(f"Parsed file is missing required columns: {missing}")

        missing_expected = set(self.columns) - set(parsed_columns)
        if missing_expected:
            missing = ", ".join(sorted(missing_expected))
            raise ValueError(f"Parsed file is missing prompt columns: {missing}")

    def get_output_columns(self) -> list[str]:
        columns = ["source", "text"]
        for field_class in self.llm_field_classes.values():
            columns += [
                c for c in field_class().get_visible_fields() if c not in columns
            ]
        for field_class in self.calc_field_classes.values():
            columns += [
                c for c in field_class().get_visible_fields() if c not in columns
            ]
        return columns
