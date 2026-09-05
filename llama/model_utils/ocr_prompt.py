from dataclasses import dataclass
from typing import Any, ClassVar

from llama.model_utils.base_prompt import BasePrompt
from llama.model_utils.prompt_file_parser import PromptFileParser

FIRST_COLUMNS = ["status", "source", "elapsed", "text"]


@dataclass
class OcrPrompt(BasePrompt):
    # -------------- ClassVars ---------------
    columns: ClassVar[list[str]] = FIRST_COLUMNS
    # ----------------------------------------

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        prompt_parser = PromptFileParser.load(kwargs["prompt"])
        self.name = prompt_parser.name
        self.description = prompt_parser.description
        self.system_msg = prompt_parser.system_msg

        self.base_headers = self._headers()
        self.base_payload = self._base_payload(**kwargs)

    def _base_payload(self, **kwargs: dict[str, Any]) -> dict:
        payload = {
            "model": kwargs["model_id"],
            "messages": [
                {"role": "system", "content": self.system_msg},
                {"role": "replace me"},
            ],
        }
        self._payload_args(**kwargs)
        return payload

    def payload(self, mime_type: str, base64_image: str) -> dict:
        target_msg = {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}",
                    },
                },
            ],
        }
        payload_ = self.base_payload
        payload_["messages"][-1] = target_msg
        return payload_
