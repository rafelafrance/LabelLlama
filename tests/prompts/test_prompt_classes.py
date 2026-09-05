"""
Construction tests for the prompt classes.

These exercise BasePrompt._payload_args, which is not covered anywhere else:
constructing a prompt must yield a sendable base payload. (This is what
guards against the `kwargs("thinking", ...)` vs `kwargs.get("thinking", ...)`
regression, which crashed every entry point at startup.)
"""

from pathlib import Path

from llama.prompts.base_prompt import Thinking
from llama.prompts.ocr_prompt import FIRST_COLUMNS, OcrPrompt
from llama.prompts.parser_prompt import ParserPrompt

PROMPT_DIR = Path("prompts")


def test_parser_prompt_base_payload() -> None:
    prompt = ParserPrompt(
        prompt=PROMPT_DIR / "herbarium_v2.md",
        model_id="test-model",
        temperature=0.1,
        max_tokens=1024,
        thinking=Thinking.DISABLE_TEMPLATE,
    )

    assert prompt.base_payload["model"] == "test-model"
    assert prompt.base_payload["temperature"] == 0.1
    assert prompt.base_payload["max_tokens"] == 1024
    assert prompt.base_payload["chat_template_kwargs"] == {"enable_thinking": False}
    assert prompt.base_payload["response_format"]
    assert prompt.columns[:4] == FIRST_COLUMNS
    assert "scientificName" in prompt.columns


def test_parser_prompt_thinking_use_server_omits_thinking_args() -> None:
    prompt = ParserPrompt(
        prompt=PROMPT_DIR / "herbarium_v2.md",
        model_id="test-model",
        thinking=Thinking.USE_SERVER,
    )

    assert "chat_template_kwargs" not in prompt.base_payload
    assert "enable_thinking" not in prompt.base_payload


def test_parser_prompt_omitted_thinking_defaults_to_use_server() -> None:
    prompt = ParserPrompt(prompt=PROMPT_DIR / "herbarium_v2.md", model_id="test-model")

    assert "chat_template_kwargs" not in prompt.base_payload
    assert "enable_thinking" not in prompt.base_payload


def test_parser_prompt_column_clash_detects_reserved_names() -> None:
    assert ParserPrompt.column_clash(["family", "text"]) == ["text"]
    assert ParserPrompt.column_clash(["family"]) == []
    assert ParserPrompt.column_clash(["status", "source"]) == ["status", "source"]


def test_ocr_prompt_base_payload() -> None:
    prompt = OcrPrompt(
        prompt=PROMPT_DIR / "ocr_v2.md",
        model_id="test-model",
        thinking=Thinking.USE_SERVER,
    )

    assert prompt.base_payload["model"] == "test-model"
    assert "response_format" not in prompt.base_payload
    assert prompt.columns == FIRST_COLUMNS
