from llama.parse2_fields.field_action import FieldAction


class Country(FieldAction):
    def preprocess(self, text: str, ocr_text: str) -> str:
        return text if text in ocr_text else ""
