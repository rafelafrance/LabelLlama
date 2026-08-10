from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llama.parser_utils.parser_prompt import ParserPrompt


@dataclass
class ParserArgs:
    prompt: ParserPrompt
    model_name: str = "qwen/qwen3.6-35b-a3b"
    api_host: str = "http://localhost:1234/v1"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 300
    threads: int = 4
