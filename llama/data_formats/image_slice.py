from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
from PIL import Image


@dataclass
class ImageArea:
    data: npt.NDArray
    west: int
    east: int
    north: int = None
    south: int = None
    text: list[str] = field(default_factory=list)

    @property
    def image(self) -> Image:
        return Image.fromarray(
            self.data[self.north : self.south, self.west : self.east]
        )

    def trim(self) -> None:
        w, e, n, s = self.west, self.east, self.north, self.south

        for w in range(self.west, self.east):
            if np.max(self.data[self.north : self.south, w]) != 0:
                break

        for e in range(self.east - 1, self.west, -1):
            if np.max(self.data[self.north : self.south, e]) != 0:
                break

        for n in range(self.north, self.south):
            if np.max(self.data[n, self.west : self.east]) != 0:
                break

        for s in range(self.south - 1, self.north, -1):
            if np.max(self.data[s, self.west : self.east]) != 0:
                break

        self.west = w
        self.east = e
        self.north = n
        self.south = s


def get_image_columns(image: npt.NDArray) -> list[ImageArea]:
    in_pic = False
    wests, easts = [], []
    for x in range(image.shape[1]):
        hi = np.max(image[:, x])
        if not in_pic and hi != 0:
            wests.append(x)
            in_pic = True
        elif in_pic and hi == 0:
            easts.append(x)
            in_pic = False
    wests = [e + int((w - e) / 2) for e, w in zip([0, *easts], wests, strict=False)]
    wests[0] = 0
    easts = [*wests[1:], image.shape[1]]
    return [
        ImageArea(image, west=w, east=e, north=0, south=image.shape[0])
        for w, e in zip(wests, easts, strict=True)
    ]


def get_labels(image: npt.NDArray, strip: ImageArea) -> list[ImageArea]:
    in_pic = False
    norths, souths = [], []
    for y in range(image.shape[0]):
        hi = np.max(image[y, strip.west : strip.east])
        if not in_pic and hi != 0:
            norths.append(y)
            in_pic = True
        elif in_pic and hi == 0:
            souths.append(y)
            in_pic = False
    norths = [n + int((s - n) / 2) for s, n in zip([0, *souths], norths, strict=False)]
    norths[0] = 0
    souths = [*norths[1:], image.shape[0]]
    labels = [
        ImageArea(image, strip.west, strip.east, n, s)
        for n, s in zip(norths, souths, strict=True)
    ]

    for lb in labels:
        lb.trim()

    return labels
