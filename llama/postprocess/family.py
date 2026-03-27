from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

import pandas as pd

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class Family(BaseField):
    taxa_csv: ClassVar[Path] = Path(__file__).parent / "terms" / "genus_to_family.csv"
    genus2fam: ClassVar[dict[str, str] | None] = None

    family: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.family = fix_values.to_str(self.family).title()

    @classmethod
    def setup_field(cls) -> None:
        rows = pd.read_csv(cls.taxa_csv).to_dict(orient="records")
        cls.genus2fam = {r["genus"]: r["family"] for r in rows}

    @classmethod
    def cross_field_score(
        cls, expect: Any, actual: Any, actual_record: dict[str, Any]
    ) -> float:
        genus = actual_record.get("scientificName", "").split()
        genus = genus[0] if len(genus) > 0 else ""
        if expect == actual:
            return 1.0
        if not expect and cls.genus2fam and cls.genus2fam.get(genus, "") == actual:
            return 1.0
        return 0.0
