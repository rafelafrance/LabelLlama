import base64
import mimetypes
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


def is_url(value: str) -> bool:
    return value.lower().startswith(("http://", "https://"))


def load_image(source: Path | str, timeout: int = 30) -> tuple[str, str]:
    """Return (base64_image, mime_type) for a local path or a remote URL."""
    if isinstance(source, str) and is_url(source):
        resp = requests.get(source, timeout=timeout)
        resp.raise_for_status()
        base64_image = base64.b64encode(resp.content).decode("utf-8")
        mime_type = resp.headers.get("Content-Type", "").split(";")[0].strip()
        if not mime_type.startswith("image/"):
            mime_type = mimetypes.guess_type(source)[0] or "application/octet-stream"
    else:
        with source.open("rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        mime_type, _ = mimetypes.guess_type(source)
        if not mime_type or not mime_type.startswith("image/"):
            mime_type = "application/octet-stream"
    return base64_image, mime_type


def _coerce(value: str) -> Path | str:
    """URLs stay strings; everything else becomes a local Path."""
    return value if is_url(value) else Path(value)


def read_sources(path: Path) -> list[Path | str]:
    """
    Parse an input file of local paths and/or remote URLs.

    One source (local path or http(s) URL) per line. Blank lines are ignored
    and lines starting with '#' are treated as comments.
    """
    values: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            values.append(line)

    seen: set[str] = set()
    out: list[Path | str] = []
    for v in values:
        if v and v not in seen:
            seen.add(v)
            out.append(_coerce(v))
    return out
