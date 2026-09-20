import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from llama.prompts.prompt import REQUIRED_COLUMNS, Prompt, Thinking

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"
DIODE = PROMPTS_DIR / "diode_one_v1.md"
OCR = PROMPTS_DIR / "ocr_v2.md"


def make_prompt(path: Path, **kwargs: dict) -> Prompt:
    kwargs.setdefault("model_id", "test-model")
    return Prompt(prompt_md=path, **kwargs)


class TestPrompt(unittest.TestCase):
    def test_init_from_markdown_01(self) -> None:
        prompt = make_prompt(DIODE)

        self.assertEqual(prompt.name, "diode_one_v1")
        self.assertTrue(prompt.description.startswith("Extract information"))
        self.assertEqual(prompt.req_fields, ["scientificName"])

    def test_columns_02(self) -> None:
        prompt = make_prompt(DIODE)

        self.assertEqual(prompt.columns[: len(REQUIRED_COLUMNS)], REQUIRED_COLUMNS)
        self.assertEqual(len(prompt.columns), len(REQUIRED_COLUMNS) + 25)
        self.assertEqual(
            prompt.columns[len(REQUIRED_COLUMNS) :][:2],
            ["scientificName", "scientificNameAuthorship"],
        )

    def test_system_msg_has_field_guidance_03(self) -> None:
        prompt = make_prompt(DIODE)

        self.assertIn("# Field Guidance", prompt.system_msg)
        self.assertIn("`scientificName`", prompt.system_msg)
        # Multi-line descriptions are collapsed to a single line
        self.assertIn("Extract the genus and species name only.", prompt.system_msg)

    def test_json_schema_required_inside_schema_04(self) -> None:
        # build_json_schema puts "required" in the json_schema
        prompt = make_prompt(DIODE)

        schema = json.loads(prompt.json_schema)
        self.assertEqual(schema["type"], "json_schema")
        inner = schema["json_schema"]
        self.assertEqual(inner["name"], "diode_one_v1")

        properties = inner["schema"]["properties"]
        self.assertEqual(len(properties), 25)
        self.assertIn("scientificName", properties)

        self.assertEqual(inner["schema"].get("required"), ["scientificName"])

    def test_json_schema_empty_without_llm_fields_05(self) -> None:
        prompt = make_prompt(OCR)

        self.assertEqual(prompt.json_schema, "")
        self.assertEqual(prompt.columns, REQUIRED_COLUMNS)

    def test_headers_api_key_06(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            prompt = make_prompt(OCR)

        self.assertEqual(prompt.headers(), {"Content-Type": "application/json"})

        with patch.dict(os.environ, {"LLM_API_KEY": "sekrit"}):
            prompt = make_prompt(OCR)

        self.assertEqual(
            prompt.headers(),
            {
                "Content-Type": "application/json",
                "Authorization": "Bearer sekrit",
            },
        )

    def test_payload_template_base_07(self) -> None:
        prompt = make_prompt(DIODE)
        payload = prompt.text_payload("hello")

        self.assertEqual(payload["model"], "test-model")
        messages = payload["messages"]
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(
            messages[-1],
            {
                "role": "user",
                "content": Prompt.text_msg + "hello",
            },
        )

    def test_payload_optional_kwargs_08(self) -> None:
        payload = make_prompt(OCR, temperature=0.2, max_tokens=100).text_payload("x")
        self.assertEqual(payload["temperature"], 0.2)
        self.assertEqual(payload["max_tokens"], 100)

        payload = make_prompt(OCR).text_payload("x")
        self.assertNotIn("temperature", payload)
        self.assertNotIn("max_tokens", payload)

    def test_image_payload_09(self) -> None:
        prompt = make_prompt(DIODE)
        payload = prompt.image_payload("image/png", "abc123")

        last = payload["messages"][-1]
        self.assertEqual(last["role"], "user")
        self.assertEqual(last["content"][0]["type"], "image_url")
        self.assertEqual(
            last["content"][0]["image_url"]["url"],
            "data:image/png;base64,abc123",
        )
        # The stored payload is not mutated by the derived payloads
        self.assertNotIn("image_url", str(prompt.text_payload("x")))

    def test_thinking_variants_10(self) -> None:
        prompt = make_prompt(OCR, thinking=Thinking.DISABLE_TEMPLATE)
        self.assertEqual(
            prompt.text_payload("x")["chat_template_kwargs"],
            {"enable_thinking": False},
        )

        prompt = make_prompt(OCR, thinking=Thinking.DISABLE_ARG)
        self.assertFalse(prompt.text_payload("x")["enable_thinking"])

        payload = make_prompt(OCR).text_payload("x")
        self.assertNotIn("chat_template_kwargs", payload)
        self.assertNotIn("enable_thinking", payload)

    def test_thinking_invalid_raises_11(self) -> None:
        with self.assertRaises(TypeError):
            make_prompt(OCR, thinking="bogus")


if __name__ == "__main__":
    unittest.main()
