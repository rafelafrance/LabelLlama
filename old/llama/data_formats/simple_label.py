from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import numpy.typing as npt
from PIL import Image


@dataclass
class SimpleLabel:
    image: Image
    path: Path
    text: list[str] = field(default_factory=list)

    @property
    def data(self) -> npt.NDArray:
        return np.asarray(self.image)

    def as_dict(self) -> dict[str, str]:
        return {"path": str(self.path), "text": "".join(self.text)}
