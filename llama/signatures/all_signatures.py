from llama.signatures.herbarium_sheet import HerbariumSheet
from llama.signatures.ocr_image import OcrImage

type AnySignature = HerbariumSheet | OcrImage

SIGNATURES = {
    "herbarium": HerbariumSheet,
    "ocr": OcrImage,
}
