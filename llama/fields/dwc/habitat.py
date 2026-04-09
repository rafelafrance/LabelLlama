from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import dedent
from llama.fields.base_field import BOTH, BaseField

HABITAT: str = dedent("""
    Collected from this habitat or environment.
    Describes the physical environment where the specimen grows.
        ✅ Include: substrate (e.g. 'dry sand', 'loamy soil'),
            vegetation type (e.g. 'open grassland'), floodplains, and life zones.
        ❌ DO NOT include associated taxa.
        ❌ DO NOT include place names, geographic features, road names, or phrases
            like 'near [named place]'. These belong to locality.
        ❌ DO NOT include details about the plant itself like height, color,
            or flowers.
    """)


@dataclass
class Habitat(BaseField):
    habitat: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.habitat = fix_values.to_str(self.habitat)

        # Remove the habitat label
        words = self.habitat.split()
        words = [s for s in words if not s.lower().startswith("habitat")]
        self.habitat = " ".join(words)


DEFAULTS = DotDict({f.name: f.default for f in fields(Habitat)})
