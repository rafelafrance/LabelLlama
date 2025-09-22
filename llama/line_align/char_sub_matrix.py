import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

# TODO: This whole messy module needs a scrub

CHAR_DB = Path(__file__).parent / "char_sub_matrix.sqlite"

CHARS = r"""
    ! " # % & ' ( ) * + , - . /
    0 1 2 3 4 5 6 7 8 9
    : ; < = > ? @
    A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
    [ \ ] ^ _ `
    a b c d e f g h i j k l m n o p q r s t u v w x y z
    { } ~ ° é — ` ` “ ” ™
    ¼ ½ ¾ ⅓ ⅔ x
    """
CHARS = "".join(["\n", " ", *CHARS.split()])


DEFAULT_FONT_SIZE = 36  # Font size in pixels
DEFAULT_IMAGE_SIZE = 40  # Size of the image containing a char


@contextmanager
def connect(db_path: Path) -> Generator:
    """Add a row factory to the normal connection context manager."""
    try:
        with sqlite3.connect(db_path) as cxn:
            cxn.row_factory = sqlite3.Row
            yield cxn
    finally:
        pass


FONT_TYPE = Any  # ImageFont | FreeTypeFont | TransposedFont | None


class Char:
    def __init__(self, char: str, image_size: int, font: FONT_TYPE) -> None:
        self.char = char
        self.image_size = image_size
        self.font = font
        self.pix = self.char_pix()
        self.h, self.w = self.char_size()

    def char_pix(self) -> npt.ArrayLike:
        """Put char pixels into a matrix."""
        image = Image.new("L", (self.image_size, self.image_size), color="black")
        draw = ImageDraw.Draw(image)
        char = " " if self.char.isspace() else self.char
        draw.text((0, 0), char, font=self.font, anchor="lt", fill="white")
        threshold = 128  # Midway point of [0, 255]
        pix = np.asarray(image.getdata()) > threshold
        pix = pix.astype("float")
        return pix

    def char_size(self) -> tuple[int, int]:
        """Get the size of the char image."""
        nz = np.nonzero(self.pix)
        if len(nz[0]) == 0:
            return 0, 0
        h = np.max(nz[0]) - np.min(nz[0]) + 1
        w = np.max(nz[1]) - np.min(nz[1]) + 1
        return h, w

    def center(self) -> None:
        """Move a char image to the center of the image."""
        y = (self.pix.shape[0] - self.h) // 2
        x = (self.pix.shape[1] - self.w) // 2
        self.pix = np.roll(self.pix, (y, x), axis=(0, 1))


# #####################################################################################
def add_chars(
    char_set: set[str],
    new_chars: set[str],
    image_size: int,
    font_path: Path,
    font_size: int,
) -> None:
    """Add characters to the character substitution matrix."""
    font = ImageFont.truetype(str(font_path), font_size)

    matrix = select_matrix(char_set)

    old_chars = {k[0] for k in matrix}
    old_chars |= {k[1] for k in matrix}

    new_chars = set(new_chars)

    calc_scores(old_chars, new_chars, matrix, image_size, font)
    insert_matrix(matrix, char_set)


def select_matrix(char_set: set[str]) -> dict:
    sql = """select * from char_sub_matrix where char_set = ?"""
    with connect(CHAR_DB) as cxn:
        rows = cxn.execute(sql, (char_set,))
    matrix = {}
    for row in rows:
        char1, char2 = row["char1"], row["char2"]
        if char1 > char2:
            char1, char2 = char2, char1
        matrix[(char1, char2)] = dict(row)
    return matrix


def insert_matrix(matrix: dict, char_set: set[str]) -> None:
    delete = """delete from char_sub_matrix where char_set = ?"""
    insert = """
        insert into char_sub_matrix
               ( char1,  char2,  char_set,  score,  sub)
        values (:char1, :char2, :char_set, :score, :sub);
        """
    batch = [
        {
            "char1": c1,
            "char2": c2,
            "char_set": char_set,
            "score": rec["score"],
            "sub": rec["sub"],
        }
        for (c1, c2), rec in matrix.items()
    ]
    with connect(CHAR_DB) as cxn:
        cxn.execute(delete, (char_set,))
        cxn.executemany(insert, batch)


def calc_scores(
    old_chars: set[str], new_chars: set[str], matrix: dict, image_size: int, font: Path
) -> None:
    """
    Calculate character substitution values.

    Substitution values go from 2 to -2. The cutoff values for converting a scores into
    substitution values are _magic_ constants.
    """
    all_chars = [Char(c, image_size, font) for c in sorted(old_chars | new_chars)]

    for i, char1 in tqdm(enumerate(all_chars)):
        char1.center()

        for char2 in all_chars[i:]:
            if char1.char not in new_chars and char2.char not in new_chars:
                score = matrix[(char1.char, char2.char)]["score"]
                sub = matrix[(char1.char, char2.char)]["sub"]
            elif char1 == char2:
                score = None
                sub = 2.0
            elif char1.char.isspace() or char2.char.isspace():
                score = np.sum(char2.pix)
                sub = -1.0 if score < 20 else -2.0  # noqa: PLR2004
            else:
                score = get_max_iou(char1.pix, char2.pix)
                sub = get_sub(score)

            matrix[(char1.char, char2.char)] = {"score": score, "sub": sub}


def get_sub(score: float) -> float:  # TODO: These values are all way too MAGIC
    if score >= 0.7:  # noqa: PLR2004
        sub = 1.0
    elif score >= 0.5:  # noqa: PLR2004
        sub = 0.0
    elif score >= 0.4:  # noqa: PLR2004
        sub = -1.0
    else:
        sub = -2.0
    return sub


def get_max_iou(pix1: npt.ArrayLike, pix2: npt.ArrayLike) -> float:
    """Get the max intersection over union of two chars."""
    max_iou = 0.0
    for y in range(pix2.shape[0]):
        for x in range(pix2.shape[1]):
            rolled = np.roll(pix2, (y, x), axis=(0, 1))
            overlap = pix1 + rolled
            union = np.sum(overlap > 0.0)
            inter = np.sum(overlap == 2.0)  # noqa: PLR2004
            curr_iou = inter / union if union else 0.0
            max_iou = max(max_iou, curr_iou)
    return max_iou


# #####################################################################################
def get(char_set: str = "default") -> dict:
    sql = """select * from char_sub_matrix where char_set = ?"""
    with connect(CHAR_DB) as cxn:
        rows = cxn.execute(sql, (char_set,))
        matrix = {f"{r['char1']}{r['char2']}": r["sub"] for r in rows}
        return matrix
