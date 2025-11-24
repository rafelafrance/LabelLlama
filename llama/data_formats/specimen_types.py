from llama.data_formats.herbarium_sheet import HerbariumSheet
from llama.data_formats.ocr_image import OcrImage

SPECIMEN_TYPES = {
    "herbarium": HerbariumSheet,
    "ocr": OcrImage,
}
