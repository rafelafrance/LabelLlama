from dataclasses import dataclass


@dataclass
class OcrModelArgs:
    api_host: str = "http://localhost:1234/v1"
    model_name: str = "chandra-ocr"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 120
    convert_html: bool = False
    threads: int = 2
