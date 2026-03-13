from llama.postprocess.field_action import FieldAction


class StateProvince(FieldAction):
    def preprocess(self, text: str, ocr_text: str) -> str:
        return text if text in ocr_text else ""
