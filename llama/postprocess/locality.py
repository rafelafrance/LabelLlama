from llama.common import fix_values
from llama.postprocess.base_action import BaseAction, FieldData

# class LocalitySig(Signature):
#     """
#     Analyze the text and extract this elevation information.
#
#     If the data field is not found in the text return an empty list.
#     Do not hallucinate.
#     """
#
#     doc_text = InputField()
#
#     locality: list[str] = OutputField(
#         default=[],
#         desc=(
#             "Get the locality from input text string. "
#             "There may be multiple phrases that describe the locality. "
#         ),
#     )


class Locality(BaseAction):
    def preprocess_field(self, field_data: FieldData) -> None:
        field_value = field_data.input_field[self.input_name]
        field_data.output_field[self.output_name] = fix_values.to_list_of_strs(
            field_value
        )
