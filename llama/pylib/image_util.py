from typing import TYPE_CHECKING

import PIL
import requests
from PIL import Image

if TYPE_CHECKING:
    from pathlib import Path

Image.MAX_IMAGE_PIXELS = 300_000_000

TOO_DAMN_SMALL = 10_000
TOO_DAMN_BIG = 32_000_000


IMAGE_ERRORS = (
    AttributeError,
    BufferError,
    ConnectionError,
    EOFError,
    FileNotFoundError,
    IOError,
    Image.DecompressionBombError,
    Image.UnidentifiedImageError,
    IndexError,
    OSError,
    RuntimeError,
    SyntaxError,
    TimeoutError,
    TypeError,
    ValueError,
    requests.exceptions.ReadTimeout,
    PIL.UnidentifiedImageError,
)

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")


def get_images(dir_: Path, limit: int | None = None) -> list[Path]:
    image_paths = sorted(
        [p for p in dir_.glob("*") if p.suffix.lower() in IMAGE_SUFFIXES]
    )
    image_paths = image_paths[:limit]

    return image_paths
