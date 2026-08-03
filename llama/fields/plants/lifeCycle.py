from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class LifeCycle(ExtractedField):
    lifeCycle: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeCycle = self.hallucinated_str(self.lifeCycle, text)
