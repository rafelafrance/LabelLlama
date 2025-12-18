from dspy import Signature

from llama.signatures.herbarium_sheet import HerbariumSheet
from llama.signatures.ocr_image import OcrImage

type AnySignature = HerbariumSheet  # | OcrImage

SIGNATURES: dict[str, AnySignature] = {
    "herbarium": HerbariumSheet,
    # "ocr": OcrImage,
}
