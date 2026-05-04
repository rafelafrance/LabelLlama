from typing import Any

from llama.fields.herbarium_fields import HERBARIUM_FIELDS
from llama.fields.insect_fields import INSECT_FIELDS

FIELD_REGISTRY: dict[str, Any] = {
    "herbarium": HERBARIUM_FIELDS,
    "insects": INSECT_FIELDS,
}
