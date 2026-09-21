from typing import TYPE_CHECKING

from llama.results.parsed_docs import ParsedDocs

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd

    from llama.prompts.prompt import Prompt

REQUIRED_COLUMNS = {"status", "source", "text"}


class FieldCleaner:
    def __init__(self, prompt: Prompt, parsed_file: Path) -> None:
        self.llm_field_classes = {f.name: f.field_class for f in prompt.llm_fields}
        self.calc_field_classes = {f.name: f.field_class for f in prompt.calc_fields}

        self.parsed_docs, _ = ParsedDocs.read_parsed_docs(parsed_file, prompt.columns)

    def validate_columns(
        self, df_columns: list[str] | pd.Index, prompt: Prompt
    ) -> None:
        missing_required = REQUIRED_COLUMNS - set(df_columns)
        if missing_required:
            missing = ", ".join(sorted(missing_required))
            raise ValueError(f"Parsed file is missing required columns: {missing}")

        missing_expected = set(prompt.columns) - set(df_columns)
        if missing_expected:
            missing = ", ".join(sorted(missing_expected))
            raise ValueError(f"Parsed file is missing prompt columns: {missing}")

    def get_llm_columns(self, df_columns: list) -> list:
        llm_columns = [c for c in df_columns if c in self.llm_field_classes]
        return llm_columns

    def get_calc_columns(self) -> list:
        calc_columns = list(self.calc_field_classes)
        return calc_columns

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
