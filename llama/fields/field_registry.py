from typing import Any

from llama.fields.herbarium_fields import HERBARIUM_FIELDS

FIELD_REGISTRY: dict[str, Any] = {
    "herbarium": HERBARIUM_FIELDS,
}
