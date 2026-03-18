from llama.postprocess.base_action import BaseAction

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
    pass
