from dataclasses import dataclass, field

import numpy as np
from PIL import Image


@dataclass
class ImageArea:
    image: Image
    west: int
    east: int
    north: int = None
    south: int = None
    text: list[str] = field(default_factory=list)

    def as_image(self) -> Image:
        return Image.fromarray(
            self.image[self.north : self.south, self.west : self.east]
        )


def get_image_columns(image: Image) -> list[ImageArea]:
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


def get_image_areas(image: Image, strip: ImageArea) -> list[ImageArea]:
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
    return [
        ImageArea(image, strip.west, strip.east, n, s)
        for n, s in zip(norths, souths, strict=True)
    ]
