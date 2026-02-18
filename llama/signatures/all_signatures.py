from llama.signatures.cas_v1 import CasV1
from llama.signatures.herbarium_sheet import HerbariumSheet

type AnySignature = HerbariumSheet | CasV1

SIGNATURES: dict[str, AnySignature] = {
    "herbarium": HerbariumSheet,
    "cas_v1": CasV1,
}
