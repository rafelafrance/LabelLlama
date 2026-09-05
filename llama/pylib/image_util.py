from pathlib import Path

import PIL
import requests
from PIL import Image

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


def has_image_suffix(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_SUFFIXES


def images_only(paths: list[Path]) -> list[Path]:
    return [p for p in paths if has_image_suffix(p)]


def image_dir(dir_: Path) -> list[Path]:
    image_paths = [p for p in dir_.glob("*") if has_image_suffix(p)]
    return image_paths


def image_glob(glob_: str) -> list[Path]:
    image_paths = [p for p in Path().glob(glob_) if has_image_suffix(p)]
    return image_paths


def get_images(dir_: Path | None = None, glob_: str | None = None) -> list[Path]:
    image_paths = []
    image_paths += image_dir(dir_) if dir_ else []
    image_paths += image_glob(glob_) if glob_ else []
    image_paths = sorted(set(image_paths))
    return image_paths
