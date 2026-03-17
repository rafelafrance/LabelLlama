from old.llama.pylib import postprocess
from llama.postprocess.field_action import FieldAction, FieldData

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


class Locality(FieldAction):
    pass
