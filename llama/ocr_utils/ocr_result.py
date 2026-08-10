from dataclasses import dataclass

from llama.ocr_utils.ocr_status import OcrStatus


@dataclass
class OcrResult:
    status: OcrStatus = OcrStatus.UNKNOWN
    source: str = ""
    elapsed: str = ""
    text: str = ""
