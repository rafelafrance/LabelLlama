from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llama.ocr_utils.ocr_prompt import OcrPrompt


@dataclass
class OcrArgs:
    prompt: OcrPrompt
    api_host: str = "http://localhost:1234/v1"
    model_name: str = "chandra-ocr"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 120
    convert_html: bool = False
    threads: int = 2
