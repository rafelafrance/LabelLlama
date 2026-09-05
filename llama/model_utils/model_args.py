from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llama.model_utils.model_prompts import OcrPrompt, ParserPrompt


@dataclass
class ExtractArgs:
    prompt: ParserPrompt
    api_host: str = "http://localhost:1234/v1"
    model_id: str = "qwen3.8-27b"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 300
    threads: int = 2


@dataclass
class OcrArgs:
    prompt: OcrPrompt
    api_host: str = "http://localhost:1234/v1"
    model_id: str = "chandra-ocr"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 120
    threads: int = 2


@dataclass
class ParserArgs:
    prompt: ParserPrompt
    model_id: str = "qwen/qwen3.6-35b-a3b"
    api_host: str = "http://localhost:1234/v1"
    temperature: float | None = None
    max_tokens: int | None = None
    timeout: int = 300
    threads: int = 4
