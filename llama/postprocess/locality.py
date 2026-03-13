from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction

# class LocalitySig(Signature):
#     """
#     Analyze the text and extract this elevation information.
#
#     If the data field is not found in the text return an empty list.
#     Do not hallucinate.
#     """
#
#     text: str = InputField()
#
#     locality: list[str] = OutputField(
#         default=[],
#         desc=(
#             "Get the locality from input text string. "
#             "There may be multiple phrases that describe the locality. "
#         ),
#     )


class Locality(FieldAction):
    def __init__(self, verbatim: str) -> None:
        super().__init__(verbatim)
        self.verbatim = verbatim

    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        locality = {"locality": " ".join(subfields["locality"].split())}
        postprocess.clean_empties(locality)
        return locality
