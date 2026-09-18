"""
Character substitution matrix for multiple sequence alignment of OCRed text.

Two characters are compared by how visually similar they are. Each character is
rendered to a black and white bitmap, then the bitmaps are slid over one another
in every direction. The score of the pair is the best *intersection over union*
(IoU) found over those translations:

    iou = overlapping pixels / pixels covered by either character

An identical pair scores 1.0, "o" against "Q" scores high, "a" against "X" scores
low and a character against a blank scores 0.0. A pair is measured once per font
then averaged over the fonts, because the ratios within one font are not directly
comparable to another font's. Only same font comparisons are ever made, the fonts
are a way of sampling how a shape can look.

The average ratio is then reduced to the coarse substitution value the alignment
actually uses (see `get_sub`), 2.0 for identical characters down to -2.0 for
characters that share hardly any ink.

Whitespace is special cased rather than measured. All whitespace renders as an
empty bitmap so its IoU is undefined: whitespace against whitespace is a perfect
match (1.0) and whitespace against anything else is no match (0.0).

Ratios are kept per font, so adding a font later costs one pass over the pairs
instead of a full rebuild.
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import numpy.typing as npt
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

from llama.line_align.align import GAP_CHAR

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Sequence

CHAR_DB = Path(__file__).parent / "char_sub_matrix.sqlite"

DEFAULT_CHAR_SET = "default"

# The fonts a character pair is rendered with. A pair's ratio is the average of
# its IoU over these fonts. They are freely licensed regular weights that cover
# most of the Latin script, and their shapes vary enough to be a decent sample:
#
#   DejaVu Serif, DejaVu Sans, DejaVu Sans Mono   (broadest coverage of symbols)
#   Liberation Serif, Liberation Sans, Liberation Mono
#   Noto Serif, Open Sans, Cantarell, Comfortaa, Montserrat, JetBrains Mono
#
FONTS: tuple[str, ...] = (
    "/usr/share/fonts/dejavu-serif-fonts/DejaVuSerif.ttf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf",
    "/usr/share/fonts/liberation-serif-fonts/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf",
    "/usr/share/fonts/liberation-mono-fonts/LiberationMono-Regular.ttf",
    "/usr/share/fonts/google-noto-vf/NotoSerif[wght].ttf",
    "/usr/share/fonts/open-sans/OpenSans-Regular.ttf",
    "/usr/share/fonts/abattis-cantarell-vf-fonts/Cantarell-VF.otf",
    "/usr/share/fonts/aajohan-comfortaa-fonts/Comfortaa-Regular.otf",
    "/usr/share/fonts/julietaula-montserrat-fonts/Montserrat-Regular.otf",
    "/usr/share/fonts/jetbrains-mono-fonts/JetBrainsMono-Regular.otf",
)

DEFAULT_FONT_SIZE = 36  # Rendered glyph height in pixels
DEFAULT_CANVAS = 48  # Size of the square bitmap that holds one character
DEFAULT_THRESHOLD = 128  # Anti aliased pixels at or above this count as ink

# Substitution values. Identical characters get IDENTICAL_SUB, characters sharing
# next to no ink get FLOOR_SUB, and the ratios in between are bucketed by these
# (minimum ratio, value) pairs, most similar first.
#
# The defaults are calibrated against the ratios the default character set
# measures, where distinct character pairs run 0.24 at the median, 0.39 at the
# 90th percentile, 0.46 at the 95th and 0.63 at the 99th. So the 1.0 bucket holds
# about the best 1% of pairs ("e"/"é", "O"/"Q", "l"/"I", "f"/"t"), the 0.0 bucket
# the next 5% ("a"/"d", "m"/"n", "Z"/"2"), the -1.0 bucket the next 18% ("o"/"0",
# "u"/"v", "s"/"8", characters that are merely of a kind) and everything else the
# floor. "o"/"0" lands in -1.0 rather than 0.0 because characters are compared at
# their rendered size and a zero is narrower than an o: IoU says they are related,
# not that they are alike.
IDENTICAL_SUB = 2.0
FLOOR_SUB = -2.0
IDENTICAL_RATIO = 1.0
DEFAULT_BUCKETS: tuple[tuple[float, float], ...] = (
    (0.65, 1.0),
    (0.45, 0.0),
    (0.30, -1.0),
)

# A private use code point: fonts draw it as the ".notdef" box, or as nothing,
# which is how `has_glyph` recognizes a character that a font does not contain.
NOTDEF_PROBE = "\ue000"

# Characters that can plausibly turn up in OCRed specimen labels. The list is
# deliberately generous, a character that is not in the matrix cannot be aligned.
# Non ASCII groups are written as escapes so that lookalikes stay tellable apart
# in the source: a three dot ellipsis is not three periods, an en dash is not a
# hyphen, a typographic quote is not an apostrophe.
CHAR_GROUPS: tuple[str, ...] = (
    "\n",  # Newline, renders blank
    " \t",  # Space and tab, both render blank
    "!\"#$%&'()*+,-./",
    "0123456789",
    ":;<=>?@[\\]^_`",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "{|}~",
    "abcdefghijklmnopqrstuvwxyz",
    "\xa1\xa2\xa3\xa5\xa7\xa9\xab\xac\xae",  # Punctuation, currency
    "\xb0\xb1\xb6\xb7\xbb",  # Degrees, plus minus, pilcrow, middle dot
    "\xbf\xb2\xb3\xb9\xbc\xbd\xbe",  # Inverted question, superscripts, fractions
    "\xd7\xf7",  # Times, divide
    # Latin-1 capitals, then smalls, U+00C0 to U+00FF
    "\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf",
    "\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf",
    "\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef",
    "\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff",
    "\u0110\u0111\u0131\u0141\u0142",  # Latin extended A, I and L with strokes
    "\u0152\u0153\u0160\u0161\u017d\u017e",  # Ligature OE, carons
    "\u2012\u2013\u2014\u2015",  # Dashes, figure dash to horizontal bar
    "\u2018\u2019\u201a\u201c\u201d\u201e",  # Typographic quotes
    "\u2020\u2021\u2022\u2026",  # Daggers, bullet, ellipsis
    "\u2030\u2032\u2033\u2039\u203a",  # Per mille, primes, single angle quotes
    "\u20ac\u2105\u2116\u2122",  # Euro, care of, numero, trademark
    "\u2153\u2154\u215b",  # Vulgar fractions
    "\u00b5\u03bc",  # Micro sign and greek mu, both spellings are used
    "\u221e\u222b\u2260\u2264\u2265\u2248",  # Infinity, integral, comparisons
    "\u221a\u2205\u0192",  # Root, empty set, function f
    "\u2640\u2642",  # Female and male symbols
    "\ufb01\ufb02",  # Fi and fl ligatures
)

# The default character set, deduplicated and in code point order.
CHARS = "".join(dict.fromkeys("".join(CHAR_GROUPS)))

Mask = npt.NDArray[np.bool_]

SCHEMA = """
create table if not exists char_sets (
    char_set    text    not null primary key,
    font_size   integer not null,
    canvas      integer not null,
    threshold   integer not null,
    fonts       text    not null,
    updated     text    not null
);

create table if not exists chars (
    char_set    text    not null,
    char        text    not null,
    primary key (char_set, char)
) without rowid;

-- One row per pair per font. Pairs are stored with char1 lexically before char2.
-- A character against itself is not stored, its ratio is implied to be 1.0.
create table if not exists char_ratios (
    char_set    text    not null,
    font        text    not null,
    char1       text    not null,
    char2       text    not null,
    ratio       real    not null,
    primary key (char_set, font, char1, char2)
) without rowid;

create index if not exists char_ratios_set_idx
    on char_ratios (char_set, char1, char2);
"""


class CharSubMatrixError(Exception):
    """Something is wrong with the character substitution matrix."""


# --------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------
@lru_cache(maxsize=64)
def _load_font(font_path: str, font_size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(font_path, font_size)


def is_blank(char: str) -> bool:
    """Return True if `char` is whitespace, which renders as nothing."""
    if len(char) != 1:
        msg = f"Not a single character: {char!r}"
        raise ValueError(msg)
    return char.isspace()


@lru_cache(maxsize=2048)
def _render_raw(
    char: str, font_path: str, font_size: int, canvas: int, threshold: int
) -> Mask:
    """Render `char`, cropped to its ink and centered on a blank canvas."""
    mask = np.zeros((canvas, canvas), dtype=bool)
    if char.isspace():
        return mask

    # Render with plenty of headroom, then crop, so nothing gets clipped.
    pad = font_size
    big = canvas + (2 * pad)
    image = Image.new("L", (big, big), color="black")
    ImageDraw.Draw(image).text(
        (pad, pad),
        char,
        font=_load_font(font_path, font_size),
        anchor="lt",
        fill="white",
    )
    ink = np.asarray(image) > threshold

    rows, cols = np.nonzero(ink)
    if not len(rows):
        return mask

    glyph = ink[rows.min() : rows.max() + 1, cols.min() : cols.max() + 1]
    height, width = glyph.shape
    if height > canvas or width > canvas:
        msg = f"{char!r} renders {width}x{height}, too large for a {canvas} canvas"
        raise ValueError(msg)

    top = (canvas - height) // 2
    left = (canvas - width) // 2
    mask[top : top + height, left : left + width] = glyph
    return mask


def render(
    char: str,
    font_path: str | Path,
    *,
    font_size: int = DEFAULT_FONT_SIZE,
    canvas: int = DEFAULT_CANVAS,
    threshold: int = DEFAULT_THRESHOLD,
) -> Mask:
    """
    Render a character as a square boolean pixel mask.

    The glyph is thresholded, cropped to its bounding box and centered on a
    `canvas` by `canvas` field of False. It is deliberately not scaled: shapes are
    compared at their rendered size, so "o" and "0" are not the same shape.
    Whitespace has no ink, so it renders as an all False mask.
    """
    if len(char) != 1:
        msg = f"Not a single character: {char!r}"
        raise ValueError(msg)
    return _render_raw(char, str(font_path), font_size, canvas, threshold).copy()


@lru_cache(maxsize=64)
def _notdef(font_path: str, font_size: int, canvas: int, threshold: int) -> Mask:
    return _render_raw(NOTDEF_PROBE, font_path, font_size, canvas, threshold)


def has_glyph(
    char: str,
    font_path: str | Path,
    *,
    font_size: int = DEFAULT_FONT_SIZE,
    canvas: int = DEFAULT_CANVAS,
    threshold: int = DEFAULT_THRESHOLD,
) -> bool:
    """
    Return True if the font really draws `char`.

    Fonts do not hold every character. A missing character comes out as the
    ".notdef" box, or as nothing at all, and neither says anything about the
    shape of the character, so those are skipped for that font. Whitespace
    answers False, it is scored by rule rather than by pixels.
    """
    if is_blank(char):
        return False

    path = str(font_path)
    mask = _render_raw(char, path, font_size, canvas, threshold)
    if not mask.any():
        return False

    notdef = _notdef(path, font_size, canvas, threshold)
    return not (notdef.shape == mask.shape and np.array_equal(notdef, mask))


# --------------------------------------------------------------------------------
# The metric
# --------------------------------------------------------------------------------
def _check_shapes(a: Mask, b: Mask) -> None:
    if a.shape != b.shape:
        msg = f"Masks must be the same shape, got {a.shape} and {b.shape}"
        raise ValueError(msg)


def max_overlap(a: Mask, b: Mask) -> int:
    """
    Return the most pixels two masks can share when slid over one another.

    Every ink pixel of `a` is paired with every ink pixel of `b` and the offset
    between the two members of each pair is tallied. The most common offset is
    the translation where the two masks agree most, its count is the overlap.

    Translations are linear, ink slid off the edge is gone. The obvious loop
    around `numpy.roll` is both slower and wrong, `roll` wraps ink around to the
    other side of the image where it can overlap a second time.
    """
    _check_shapes(a, b)
    rows_a, cols_a = np.nonzero(a)
    rows_b, cols_b = np.nonzero(b)
    if not len(rows_a) or not len(rows_b):
        return 0

    height, width = a.shape
    rows = (rows_a[:, None] - rows_b[None, :]).ravel() + (height - 1)
    cols = (cols_a[:, None] - cols_b[None, :]).ravel() + (width - 1)
    offsets = rows * ((2 * width) - 1) + cols
    return int(np.bincount(offsets).max())


def max_iou(a: Mask, b: Mask) -> float:
    """
    Return the best intersection over union of two masks in any translation.

    Whitespace is dealt with here rather than by the caller: two masks with no
    ink are a perfect match, one mask with no ink is no match at all.
    """
    _check_shapes(a, b)
    ink_a = int(a.sum())
    ink_b = int(b.sum())
    if not ink_a and not ink_b:
        return IDENTICAL_RATIO
    if not ink_a or not ink_b:
        return 0.0

    overlap = max_overlap(a, b)
    union = ink_a + ink_b - overlap
    return overlap / union


def get_sub(
    ratio: float,
    *,
    identical: float = IDENTICAL_SUB,
    buckets: Sequence[tuple[float, float]] = DEFAULT_BUCKETS,
    floor: float = FLOOR_SUB,
) -> float:
    """
    Return the substitution value for a visual similarity ratio.

    `buckets` are (minimum ratio, value) pairs ordered from most to least
    similar. A ratio that reaches none of them gets `floor`, a perfect ratio gets
    `identical`.
    """
    if ratio >= IDENTICAL_RATIO:
        return identical

    for minimum, value in buckets:
        if ratio >= minimum:
            return value
    return floor


# --------------------------------------------------------------------------------
# The database
# --------------------------------------------------------------------------------
@contextmanager
def _connect(db: Path | str | None = None) -> Iterator[sqlite3.Connection]:
    """Open the matrix database, committing the transaction on the way out."""
    cxn = sqlite3.connect(_db_path(db))
    cxn.row_factory = sqlite3.Row
    try:
        yield cxn
        cxn.commit()
    finally:
        cxn.close()


def _db_path(db: Path | str | None) -> Path:
    return CHAR_DB if db is None else Path(db)


def _require_db(db: Path | str | None) -> Path:
    """Return the database path, complaining if the matrix has not been built."""
    path = _db_path(db)
    if not path.is_file():
        msg = (
            f"There is no character substitution matrix at {path}. Build one with "
            "llama/line_align/build_char_sub_matrix.py"
        )
        raise CharSubMatrixError(msg)
    return path


def _init_schema(cxn: sqlite3.Connection) -> None:
    cxn.executescript(SCHEMA)


def _canonical(char1: str, char2: str) -> tuple[str, str]:
    """Return a pair with the lexically first character first."""
    return (char1, char2) if char1 <= char2 else (char2, char1)


def _clean_chars(chars: str | Iterable[str]) -> list[str]:
    """Return the characters to work on, deduplicated and in code point order."""
    candidates = chars if isinstance(chars, str) else "".join(chars)
    for char in candidates:
        if len(char) != 1:
            msg = f"Not a single character: {char!r}"
            raise ValueError(msg)
        if char == GAP_CHAR:
            msg = f"{GAP_CHAR!r} is the alignment gap character, it cannot be scored"
            raise ValueError(msg)
    return sorted(dict.fromkeys(candidates))


def _font_paths(fonts: Sequence[str | Path]) -> list[str]:
    """Return the usable fonts, skipping files that do not exist and repeats."""
    paths: list[str] = []
    seen: set[str] = set()
    for font in fonts:
        path = Path(font)
        if not path.is_file():
            logging.warning("Not a font file: %s", path)
            continue
        if path.name in seen:
            logging.warning("Repeated font name: %s", path)
            continue
        seen.add(path.name)
        paths.append(str(path))
    if not paths:
        msg = "None of the given fonts could be opened"
        raise CharSubMatrixError(msg)
    return paths


def _list_chars(cxn: sqlite3.Connection, char_set: str) -> set[str]:
    sql = "select char from chars where char_set = ?"
    return {row[0] for row in cxn.execute(sql, (char_set,))}


# --------------------------------------------------------------------------------
# Measuring
# --------------------------------------------------------------------------------
_INSERT_RATIO = (
    "insert or replace into char_ratios (char_set, font, char1, char2, ratio)"
    " values (?, ?, ?, ?, ?)"
)


def _covered_chars(
    chars: Sequence[str], font_path: str, font_size: int, canvas: int, threshold: int
) -> list[str]:
    """Return the characters of `chars` that this font can be used to compare."""
    return [
        char
        for char in chars
        if char.isspace()
        or has_glyph(
            char, font_path, font_size=font_size, canvas=canvas, threshold=threshold
        )
    ]


def _pairs(chars: Sequence[str]) -> list[tuple[str, str]]:
    """Return every distinct pair of characters, lexically ordered."""
    return [_canonical(c1, c2) for c1, c2 in combinations(sorted(set(chars)), 2)]


def _known_pairs(cxn: sqlite3.Connection, char_set: str) -> set[tuple[str, str, str]]:
    """Return the (font, char1, char2) triples already measured for a character set."""
    sql = "select font, char1, char2 from char_ratios where char_set = ?"
    return {(row[0], row[1], row[2]) for row in cxn.execute(sql, (char_set,))}


def _measure(
    pairs: Sequence[tuple[str, str]],
    *,
    font_path: str,
    font_size: int,
    canvas: int,
    threshold: int,
    progress: bool,
) -> Iterator[tuple[str, str, float]]:
    """Yield the (char1, char2, ratio) measurements of one font."""
    masks: dict[str, Mask] = {}

    def mask(char: str) -> Mask:
        if char not in masks:
            masks[char] = _render_raw(char, font_path, font_size, canvas, threshold)
        return masks[char]

    bar = tqdm(pairs, desc=f"pairs ({Path(font_path).name})", disable=not progress)
    for char1, char2 in bar:
        yield char1, char2, max_iou(mask(char1), mask(char2))


def add_chars(
    chars: str | Iterable[str] = CHARS,
    char_set: str = DEFAULT_CHAR_SET,
    *,
    fonts: Sequence[str | Path] = FONTS,
    font_size: int = DEFAULT_FONT_SIZE,
    canvas: int = DEFAULT_CANVAS,
    threshold: int = DEFAULT_THRESHOLD,
    force: bool = False,
    db: Path | str | None = None,
    progress: bool = True,
) -> list[str]:
    """
    Add characters to the substitution matrix.

    Every pair of characters in the set is measured in every font, unless that
    pair has already been measured in that font, in which case it is kept. Adding
    a character, or adding a font, therefore only pays for the measurements that
    are genuinely new.

    A character that no font can draw is left out of the set and reported as a
    warning, it would otherwise join the matrix with no measurements at all.

    Returns the characters in `char_set` once done.
    """
    new_chars = _clean_chars(chars)
    font_paths = _font_paths(fonts)

    with _connect(db) as cxn:
        _init_schema(cxn)
        _check_settings(cxn, char_set, font_size, canvas, threshold, force=force)

        everything = sorted(_list_chars(cxn, char_set) | set(new_chars))
        known = _known_pairs(cxn, char_set)
        drawn: set[str] = set()

        for font_path in font_paths:
            font = Path(font_path).name
            covered = _covered_chars(
                everything, font_path, font_size, canvas, threshold
            )
            drawn.update(covered)

            todo = [pair for pair in _pairs(covered) if (font, *pair) not in known]
            if not todo:
                logging.info("Nothing new to measure for %s", font)
                continue

            rows = [
                (char_set, font, char1, char2, ratio)
                for char1, char2, ratio in _measure(
                    todo,
                    font_path=font_path,
                    font_size=font_size,
                    canvas=canvas,
                    threshold=threshold,
                    progress=progress,
                )
            ]
            cxn.executemany(_INSERT_RATIO, rows)
            logging.info("Measured %d pairs in %s", len(rows), font)

        dropped = sorted(set(new_chars) - drawn)
        if dropped:
            logging.warning(
                "None of these fonts can draw %s, it is not in %s",
                "".join(dropped),
                char_set,
            )

        cxn.executemany(
            "insert or ignore into chars (char_set, char) values (?, ?)",
            [(char_set, char) for char in new_chars if char in drawn],
        )
        _save_settings(
            cxn, char_set, font_size, canvas, threshold, font_paths=font_paths
        )
        return sorted(_list_chars(cxn, char_set))


def rebuild(
    chars: str | Iterable[str] = CHARS,
    char_set: str = DEFAULT_CHAR_SET,
    **kwargs: Any,
) -> list[str]:
    """Throw away a character set and measure it again from scratch."""
    delete_char_set(char_set, db=kwargs.get("db"))
    return add_chars(chars, char_set, **kwargs)


def delete_char_set(char_set: str, *, db: Path | str | None = None) -> int:
    """
    Remove a character set and everything measured for it, returning the rows deleted.

    A matrix that does not exist yet has nothing to delete, so this answers 0.
    """
    path = _db_path(db)
    if not path.is_file():
        return 0

    with _connect(path) as cxn:
        _init_schema(cxn)
        measured = cxn.execute(
            "delete from char_ratios where char_set = ?", (char_set,)
        ).rowcount
        kept = cxn.execute("delete from chars where char_set = ?", (char_set,)).rowcount
        cxn.execute("delete from char_sets where char_set = ?", (char_set,))
        return measured + kept


def _settings(cxn: sqlite3.Connection, char_set: str) -> sqlite3.Row | None:
    sql = "select * from char_sets where char_set = ?"
    return cxn.execute(sql, (char_set,)).fetchone()


def _check_settings(
    cxn: sqlite3.Connection,
    char_set: str,
    font_size: int,
    canvas: int,
    threshold: int,
    *,
    force: bool,
) -> None:
    """Complain when the rendering settings of an existing set are being changed."""
    settings = _settings(cxn, char_set)
    if settings is None or force:
        return

    wanted = {"font_size": font_size, "canvas": canvas, "threshold": threshold}
    changed = [
        f"{name} {settings[name]} -> {value}"
        for name, value in wanted.items()
        if settings[name] != value
    ]
    if changed:
        msg = (
            f"Character set {char_set!r} was measured with other rendering settings "
            f"({', '.join(changed)}). Ratios from one setting are not comparable to "
            "another. Rebuild the set, or pass force=True to go ahead anyway."
        )
        raise CharSubMatrixError(msg)


def _save_settings(
    cxn: sqlite3.Connection,
    char_set: str,
    font_size: int,
    canvas: int,
    threshold: int,
    *,
    font_paths: Sequence[str],
) -> None:
    sql = """
        insert into char_sets (char_set, font_size, canvas, threshold, fonts, updated)
        values (?, ?, ?, ?, ?, ?)
        on conflict (char_set) do update set
            font_size = excluded.font_size,
            canvas    = excluded.canvas,
            threshold = excluded.threshold,
            fonts     = excluded.fonts,
            updated   = excluded.updated
        """
    fonts = "\n".join(Path(path).name for path in font_paths)
    cxn.execute(
        sql, (char_set, font_size, canvas, threshold, fonts, str(datetime.now()))
    )


# --------------------------------------------------------------------------------
# Querying
# --------------------------------------------------------------------------------
def build_info(
    char_set: str = DEFAULT_CHAR_SET, *, db: Path | str | None = None
) -> dict | None:
    """Return how a character set was built, or None if it does not exist."""
    path = _require_db(db)
    with _connect(path) as cxn:
        _init_schema(cxn)
        settings = _settings(cxn, char_set)
        return dict(settings) if settings else None


def list_char_sets(*, db: Path | str | None = None) -> list[str]:
    """Return the character sets in the matrix."""
    path = _require_db(db)
    with _connect(path) as cxn:
        _init_schema(cxn)
        sql = "select distinct char_set from chars order by char_set"
        return [row[0] for row in cxn.execute(sql)]


def list_chars(
    char_set: str = DEFAULT_CHAR_SET, *, db: Path | str | None = None
) -> list[str]:
    """Return the characters of a character set, in code point order."""
    path = _require_db(db)
    with _connect(path) as cxn:
        _init_schema(cxn)
        return sorted(_list_chars(cxn, char_set))


def missing_chars(
    chars: str | Iterable[str],
    char_set: str = DEFAULT_CHAR_SET,
    *,
    db: Path | str | None = None,
) -> list[str]:
    """
    Return the characters that are not in the matrix yet.

    Check a text with this before starting a job. A character the matrix does not
    know cannot be scored against anything, so aligning it would fail halfway
    through with no result at all.
    """
    candidates = chars if isinstance(chars, str) else "".join(chars)
    known = set(list_chars(char_set, db=db))
    return [char for char in dict.fromkeys(candidates) if char not in known]


def get_ratios(
    char_set: str = DEFAULT_CHAR_SET,
    *,
    db: Path | str | None = None,
) -> dict[tuple[str, str], float]:
    """
    Return the average visual similarity of every pair in a character set.

    Keys are (char1, char2) with char1 lexically first, including the (char, char)
    pairs of the characters themselves, which are always 1.0.
    """
    path = _require_db(db)
    with _connect(path) as cxn:
        _init_schema(cxn)
        chars = _list_chars(cxn, char_set)
        if not chars:
            msg = (
                f"Character set {char_set!r} has no characters. Build it with "
                "llama/line_align/build_char_sub_matrix.py"
            )
            raise CharSubMatrixError(msg)

        sql = """
            select char1, char2, avg(ratio) as ratio
            from char_ratios
            where char_set = ?
            group by char1, char2
            """
        ratios = {
            _canonical(row[0], row[1]): row[2] for row in cxn.execute(sql, (char_set,))
        }
        ratios.update({(char, char): IDENTICAL_RATIO for char in chars})
        return ratios


def get(
    char_set: str = DEFAULT_CHAR_SET,
    *,
    db: Path | str | None = None,
    identical: float = IDENTICAL_SUB,
    buckets: Sequence[tuple[float, float]] = DEFAULT_BUCKETS,
    floor: float = FLOOR_SUB,
) -> dict[str, float]:
    """
    Return the substitution values of every pair in a character set.

    Keys are the two characters of the pair concatenated, lexically first
    character first, so `matrix["ab"]` is the value of "a" against "b" and there
    is no "ba". Values are the average IoU of the pair over the fonts, bucketed by
    `get_sub`.
    """
    return {
        f"{char1}{char2}": get_sub(
            ratio, identical=identical, buckets=buckets, floor=floor
        )
        for (char1, char2), ratio in get_ratios(char_set, db=db).items()
    }
