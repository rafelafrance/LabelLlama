import contextlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldData:
    input_field: dict[str, Any]
    output_field: dict[str, Any] = field(default_factory=dict)


class BaseAction:
    def __init__(self, input_name: str) -> None:
        self.predictor = None
        self.input_name = input_name

        name = self.__class__.__name__
        self.output_name = name[0].lower() + name[1:]

    def all_output_names(self) -> list[str]:
        return [self.output_name]

    def preprocess_field(self, field_data: FieldData) -> None:
        pass

    def predict(self, field_data: FieldData) -> None:
        pass

    def postprocess(self, field_data: FieldData) -> None:
        pass

    def common_preprocess(self, field_data: FieldData) -> None:
        """
        Fix common problems with strings after a language model mangles them.

        Field specific preprocessing happens after this.
        """
        field_value = field_data.input_field[self.output_name]

        # Handle a stringified array
        if field_value.startswith("[") and field_value.endswith("]"):
            if len(field_value) > 1 and field_value[1] == "'":
                field_value = field_value.replace('"', r"\"")
                field_value = field_value.replace("'", '"')

            with contextlib.suppress(json.decoder.JSONDecodeError):
                field_value = json.loads(field_value)

        # Convert an array into a string
        if isinstance(field_value, list):
            field_value = " ".join(field_value)

        # Remove common empty field notations
        if field_value in ("[]", '""', "''"):
            field_value = ""

        # Remove leading and trailing quotes
        if (
            field_value.startswith('"')
            and field_value.endswith('"')
            and len(field_value) > 1
        ):
            field_value = field_value.removeprefix('"')
            field_value = field_value.removesuffix('"')

        field_data.output_field[self.output_name] = field_value

    def __call__(self, field_data: FieldData) -> None:
        self.common_preprocess(field_data)
        self.preprocess_field(field_data)
        self.predict(field_data)
        self.postprocess(field_data)
