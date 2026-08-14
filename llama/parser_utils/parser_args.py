from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llama.parser_utils.parser_prompt import ParserPrompt


@dataclass
class ParserArgs:
    prompt: ParserPrompt
    model_id: str = "qwen/qwen3.6-35b-a3b"
    api_host: str = "http://localhost:1234/v1"
    temperature: float | None = None
    max_tokens: int | None = None
    timeout: int = 300
    threads: int = 4
