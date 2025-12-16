from llama.data_formats.herbarium_sheet import HerbariumSheet
from llama.data_formats.ocr_image import OcrImage

type AnySignature = HerbariumSheet | OcrImage

SIGNATURES = {
    "herbarium": HerbariumSheet,
    "ocr": OcrImage,
}
