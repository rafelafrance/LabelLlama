import unittest
from pathlib import Path

from llama.calc_fields.event.eventDate import EventDate
from llama.llm_fields.taxon.scientificName import ScientificName
from llama.prompts.field_action import FieldAction
from llama.prompts.prompt_markdown_parser import PromptMarkdownParser


class TestFieldAction(unittest.TestCase):
    def test_llm_field_01(self) -> None:
        """A prompted field is an LLM action on the text."""
        fa = FieldAction("../llama/llm_fields/taxon/scientificName.py")

        self.assertEqual(fa.name, "scientificName")
        self.assertIsInstance(fa.module, Path)
        self.assertIs(fa.field_class, ScientificName)
        self.assertEqual(fa.columns, fa.field_class().get_field_names())
        self.assertIn("scientificName", fa.columns)

    def test_calc_field_02(self) -> None:
        """An absent field is a CALC action computed from the record."""
        fa = FieldAction("../llama/calc_fields/event/eventDate.py")

        self.assertEqual(fa.name, "eventDate")
        self.assertIs(fa.field_class, EventDate)
        self.assertIn("eventDate", fa.columns)

    def test_links_from_real_prompt_03(self) -> None:
        """Every LLM field link in a shipped prompt must import cleanly."""
        prompt_path = (
            Path(__file__).resolve().parents[2] / "prompts" / "diode_one_v1.md"
        )
        parser = PromptMarkdownParser(prompt_path)

        for field in parser.llm_fields:
            self.assertTrue(field.columns)


if __name__ == "__main__":
    unittest.main()
