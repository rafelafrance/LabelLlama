"""Tests for the character substitution matrix."""

import logging
import sqlite3
import tempfile
import unittest
from pathlib import Path
from typing import ClassVar
from unittest import mock

import numpy as np

from llama.line_align import char_sub_matrix


class TestCharSubMatrix(unittest.TestCase):
    """The metric, the rendering, the bucketing and the database."""

    fonts: ClassVar[list[str]] = [
        font for font in char_sub_matrix.FONTS if Path(font).is_file()
    ]

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "matrix.sqlite"
        self.fonts = self.fonts[:2]
        self._build("ab\n ")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    # ------------------------------------------------------------------- helpers
    def _build(self, chars: str, **kwargs: object) -> list[str]:
        kwargs.setdefault("fonts", self.fonts)
        kwargs.setdefault("db", self.db)
        kwargs.setdefault("progress", False)
        return char_sub_matrix.add_chars(chars, **kwargs)

    def _measured(self, chars: str, **kwargs: object) -> int:
        """Add characters, returning how many pair measurements were actually done."""
        with mock.patch.object(
            char_sub_matrix, "_measure", wraps=char_sub_matrix._measure
        ) as spy:
            self._build(chars, **kwargs)
        return sum(len(call.args[0]) for call in spy.call_args_list)

    def _rows(self) -> list[tuple]:
        with sqlite3.connect(self.db) as cxn:
            rows = cxn.execute("select font, char1, char2 from char_ratios").fetchall()
        cxn.close()
        return rows

    @staticmethod
    def _blank(width: int = 3) -> np.ndarray:
        return np.zeros((width, width), dtype=bool)

    @staticmethod
    def _pixels(pixels: list[tuple[int, int]], width: int = 3) -> np.ndarray:
        mask = TestCharSubMatrix._blank(width)
        mask[[row for row, _ in pixels], [col for _, col in pixels]] = True
        return mask

    @staticmethod
    def _reference_iou(a: np.ndarray, b: np.ndarray) -> float:
        """Return the metric straight from its definition, slowly, for testing."""
        height, width = a.shape
        ink_a = int(a.sum())
        ink_b = int(b.sum())
        best = 0.0
        for dy in range(-height + 1, height):
            for dx in range(-width + 1, width):
                moved = np.zeros_like(b)
                rows, cols = np.nonzero(b)
                rows, cols = rows + dy, cols + dx
                kept = (rows >= 0) & (rows < height) & (cols >= 0) & (cols < width)
                moved[rows[kept], cols[kept]] = True
                overlap = int((a & moved).sum())
                best = max(best, overlap / (ink_a + ink_b - overlap))
        return best

    # ------------------------------------------------------------------- max_iou
    def test_max_iou_01(self) -> None:
        # One pixel is the whole of the other, wherever it is.
        pix1 = self._pixels([(1, 1)])
        pix2 = self._pixels([(0, 0)])
        self.assertEqual(char_sub_matrix.max_iou(pix1, pix2), 1.0)

    def test_max_iou_02(self) -> None:
        # A shape is identical to itself however far it has been slid.
        pix1 = self._pixels([(1, 1), (1, 2)])
        pix2 = self._pixels([(0, 0), (0, 1)])
        self.assertEqual(char_sub_matrix.max_iou(pix1, pix2), 1.0)

    def test_max_iou_03(self) -> None:
        # A bar standing up against a bar lying down shares one pixel of five.
        pix1 = self._pixels([(0, 1), (1, 1), (2, 1)])
        pix2 = self._pixels([(0, 0), (0, 1), (0, 2)])
        self.assertEqual(char_sub_matrix.max_iou(pix1, pix2), 0.2)

    def test_max_iou_04(self) -> None:
        # The best translation of two masks that share no shape is the overlap of
        # one of them, their union is bigger than either.
        one = self._pixels([(0, 0), (0, 1)], width=5)
        two = self._pixels([(3, 3), (4, 3), (4, 4)], width=5)
        self.assertEqual(char_sub_matrix.max_overlap(one, two), 2)
        self.assertEqual(char_sub_matrix.max_iou(one, two), 2 / 3)

    def test_max_iou_05(self) -> None:
        # Whitespace: two blanks match perfectly, a blank never matches ink.
        ink = self._pixels([(1, 1), (1, 2)])
        self.assertEqual(char_sub_matrix.max_iou(self._blank(), self._blank()), 1.0)
        self.assertEqual(char_sub_matrix.max_iou(self._blank(), ink), 0.0)
        self.assertEqual(char_sub_matrix.max_iou(ink, self._blank()), 0.0)
        self.assertEqual(char_sub_matrix.max_overlap(self._blank(), ink), 0)

    def test_max_iou_06(self) -> None:
        # Two marks 35 apart. Sliding one off the edge must not wrap it around to
        # the other side and let it overlap a second time, which is what np.roll does.
        a = self._pixels([(0, 3), (0, 38)], width=40)
        b = self._pixels([(0, 30), (0, 35)], width=40)
        self.assertEqual(char_sub_matrix.max_iou(a, b), 1 / 3)

    def test_max_iou_07(self) -> None:
        rng = np.random.default_rng(7)
        for _ in range(15):
            a = rng.random((6, 7)) < 0.35
            b = rng.random((6, 7)) < 0.35
            if not a.any() or not b.any():
                continue
            self.assertAlmostEqual(
                char_sub_matrix.max_iou(a, b), self._reference_iou(a, b), places=12
            )

    def test_max_iou_08(self) -> None:
        # The same shape, placed anywhere in the canvas, is a perfect match.
        rng = np.random.default_rng(11)
        for _ in range(10):
            shape = rng.random((4, 4)) < 0.5
            if not shape.any():
                continue
            here = self._blank(10)
            there = self._blank(10)
            here[0:4, 0:4] = shape
            there[3:7, 5:9] = shape
            self.assertAlmostEqual(char_sub_matrix.max_iou(here, there), 1.0, places=12)

    def test_max_iou_09(self) -> None:
        rng = np.random.default_rng(23)
        for _ in range(10):
            a = rng.random((5, 5)) < 0.4
            b = rng.random((5, 5)) < 0.4
            if not a.any() or not b.any():
                continue
            self.assertAlmostEqual(
                char_sub_matrix.max_iou(a, b), char_sub_matrix.max_iou(b, a), places=12
            )

    def test_max_iou_10(self) -> None:
        with self.assertRaisesRegex(ValueError, "same shape"):
            char_sub_matrix.max_iou(self._blank(), self._blank(7))
        with self.assertRaisesRegex(ValueError, "same shape"):
            char_sub_matrix.max_overlap(self._blank(), self._blank(7))

    # ------------------------------------------------------------------ rendering
    def test_render_11(self) -> None:
        for char in " \t\n":
            mask = char_sub_matrix.render(char, self.fonts[0])
            self.assertEqual(mask.shape, (char_sub_matrix.DEFAULT_CANVAS,) * 2)
            self.assertFalse(mask.any(), f"{char!r} should render as nothing")
            self.assertEqual(char_sub_matrix.max_iou(mask, mask), 1.0)

    def test_render_12(self) -> None:
        # The ink is cropped to its bounding box, so it reaches the edge of the
        # canvas, and it is centered rather than rolled around.
        mask = char_sub_matrix.render("H", self.fonts[0], canvas=60)
        rows, cols = np.nonzero(mask)
        self.assertLessEqual(abs(int(rows.min()) - int(60 - 1 - rows.max())), 1)
        self.assertLessEqual(abs(int(cols.min()) - int(60 - 1 - cols.max())), 1)

    def test_render_13(self) -> None:
        with self.assertRaisesRegex(ValueError, "too large"):
            char_sub_matrix.render("W", self.fonts[0], canvas=8)

    def test_render_14(self) -> None:
        # Masks come out of a cache, so callers must not be able to spoil it.
        char_sub_matrix.render("o", self.fonts[0])[:] = False
        self.assertTrue(char_sub_matrix.render("o", self.fonts[0]).any())

    def test_render_15(self) -> None:
        for not_a_char in ("", "ab", "\u00e9\u00e9"):
            with self.assertRaisesRegex(ValueError, "single character"):
                char_sub_matrix.render(not_a_char, self.fonts[0])
        with self.assertRaisesRegex(ValueError, "single character"):
            char_sub_matrix.is_blank("ab")

    def test_render_16(self) -> None:
        wide = int(char_sub_matrix.render("W", self.fonts[0]).sum())
        narrow = int(char_sub_matrix.render("i", self.fonts[0]).sum())
        self.assertGreater(wide, narrow)
        self.assertNotEqual(
            char_sub_matrix.max_iou(
                char_sub_matrix.render("W", self.fonts[0]),
                char_sub_matrix.render("i", self.fonts[0]),
            ),
            1.0,
        )

    # ------------------------------------------------------------------ has_glyph
    def test_has_glyph_17(self) -> None:
        for char in "Aa0.-–Çµ":
            self.assertTrue(char_sub_matrix.has_glyph(char, self.fonts[0]), char)

    def test_has_glyph_18(self) -> None:
        for char in " \t\n":
            self.assertFalse(char_sub_matrix.has_glyph(char, self.fonts[0]), char)

    def test_has_glyph_19(self) -> None:
        # A private use code point: no font has it, so it comes out as .notdef.
        self.assertFalse(char_sub_matrix.has_glyph("\uf8ff", self.fonts[0]))
        self.assertFalse(
            char_sub_matrix.has_glyph(char_sub_matrix.NOTDEF_PROBE, self.fonts[0])
        )

    # --------------------------------------------------------------------- get_sub
    def test_get_sub_20(self) -> None:
        self.assertEqual(char_sub_matrix.get_sub(1.0), char_sub_matrix.IDENTICAL_SUB)
        self.assertEqual(char_sub_matrix.get_sub(0.99999), 1.0)

    def test_get_sub_21(self) -> None:
        strong, medium, weak = char_sub_matrix.DEFAULT_BUCKETS
        self.assertEqual(char_sub_matrix.get_sub(strong[0]), 1.0)
        self.assertEqual(char_sub_matrix.get_sub(strong[0] - 0.001), 0.0)
        self.assertEqual(char_sub_matrix.get_sub(medium[0]), 0.0)
        self.assertEqual(char_sub_matrix.get_sub(medium[0] - 0.001), -1.0)
        self.assertEqual(char_sub_matrix.get_sub(weak[0]), -1.0)
        self.assertEqual(
            char_sub_matrix.get_sub(weak[0] - 0.001), char_sub_matrix.FLOOR_SUB
        )

    def test_get_sub_22(self) -> None:
        buckets = ((0.5, -5.0), (0.1, -9.0))
        self.assertEqual(char_sub_matrix.get_sub(0.6, buckets=buckets), -5.0)
        self.assertEqual(char_sub_matrix.get_sub(0.3, buckets=buckets), -9.0)
        self.assertEqual(
            char_sub_matrix.get_sub(0.05, buckets=buckets), char_sub_matrix.FLOOR_SUB
        )
        self.assertEqual(char_sub_matrix.get_sub(0.2, buckets=(), floor=-7.0), -7.0)
        self.assertEqual(char_sub_matrix.get_sub(1.0, identical=9.0), 9.0)

    # ------------------------------------------------------------------- add_chars
    def test_add_chars_23(self) -> None:
        self.assertEqual(char_sub_matrix.list_chars(db=self.db), sorted("ab\n "))
        self.assertEqual(char_sub_matrix.list_char_sets(db=self.db), ["default"])
        self.assertEqual(len(self._rows()), 2 * 6)  # two fonts, four characters

    def test_add_chars_24(self) -> None:
        # Every pair of the set has a ratio, including a character against itself.
        chars = char_sub_matrix.list_chars(db=self.db)
        ratios = char_sub_matrix.get_ratios(db=self.db)
        wanted = {(c1, c2) for i, c1 in enumerate(chars) for c2 in chars[i:]}
        self.assertEqual(set(ratios), wanted)
        for char in chars:
            self.assertEqual(ratios[(char, char)], 1.0)

    def test_add_chars_25(self) -> None:
        # A pair is stored once, with the lexically first character first.
        stored = {(c1, c2) for _, c1, c2 in self._rows()}
        self.assertTrue(stored)
        for char1, char2 in stored:
            self.assertLess(char1, char2)
        self.assertEqual(
            set(char_sub_matrix.get(db=self.db)),
            {c1 + c2 for c1, c2 in stored}
            | {c + c for c in char_sub_matrix.list_chars(db=self.db)},
        )

    def test_add_chars_26(self) -> None:
        # Whitespace is scored by rule, not by pixels.
        ratios = char_sub_matrix.get_ratios(db=self.db)
        self.assertEqual(ratios[("\n", " ")], 1.0)
        self.assertEqual(ratios[(" ", "a")], 0.0)
        self.assertEqual(ratios[("\n", "b")], 0.0)
        subs = char_sub_matrix.get(db=self.db)
        self.assertEqual(subs["\n "], char_sub_matrix.IDENTICAL_SUB)
        self.assertEqual(subs[" a"], char_sub_matrix.FLOOR_SUB)

    def test_add_chars_27(self) -> None:
        # A new character costs the pairs it is in, and nothing that is measured.
        measured = self._measured("abc")
        self.assertEqual(
            measured, 2 * 4
        )  # "c" against the four characters already there
        self.assertEqual(len(self._rows()), 2 * 10)  # five characters, two fonts
        self.assertEqual(self._measured("abc"), 0)  # nothing left to do

    def test_add_chars_28(self) -> None:
        # A new font costs the pairs of every character once, and nothing else.
        fresh = Path(self.tmp.name) / "fresh.sqlite"
        self._build("abcd", db=fresh, fonts=self.fonts[:1])
        self.assertEqual(self._measured("abcd", db=fresh, fonts=self.fonts[:2]), 6)
        self.assertEqual(
            self._build("abcd", db=fresh, fonts=self.fonts[:2]), sorted("abcd")
        )

    def test_add_chars_29(self) -> None:
        self._build("x")
        self.assertEqual(char_sub_matrix.list_chars(db=self.db), sorted("ab\n x"))

    def test_add_chars_30(self) -> None:
        # No font can draw a private use character, so it never joins the set.
        with self.assertLogs(level=logging.WARNING):
            self._build("a\uf8ff")
        self.assertEqual(char_sub_matrix.list_chars(db=self.db), sorted("ab\n "))

    def test_add_chars_31(self) -> None:
        with self.assertRaisesRegex(ValueError, "gap character"):
            char_sub_matrix.add_chars(
                f"a{char_sub_matrix.GAP_CHAR}", db=self.db, progress=False
            )

    def test_add_chars_32(self) -> None:
        # Ratios of two settings cannot be averaged together.
        with self.assertRaisesRegex(
            char_sub_matrix.CharSubMatrixError, "other rendering"
        ):
            self._build("abc", canvas=64)
        self._build("abc", canvas=64, force=True)
        self.assertEqual(char_sub_matrix.list_chars(db=self.db), sorted("abc\n "))

    def test_add_chars_33(self) -> None:
        # A second character set lives alongside the first.
        char_sub_matrix.add_chars(
            "qr", "symbols", fonts=self.fonts, db=self.db, progress=False
        )
        self.assertEqual(
            char_sub_matrix.list_char_sets(db=self.db), ["default", "symbols"]
        )
        self.assertEqual(char_sub_matrix.list_chars("symbols", db=self.db), ["q", "r"])
        self.assertEqual(
            set(char_sub_matrix.get("symbols", db=self.db)), {"qq", "qr", "rr"}
        )

    def test_add_chars_34(self) -> None:
        expected = len(self._rows()) + len(char_sub_matrix.list_chars(db=self.db))
        self.assertEqual(
            char_sub_matrix.delete_char_set("default", db=self.db), expected
        )
        self.assertEqual(char_sub_matrix.list_char_sets(db=self.db), [])
        self.assertEqual(char_sub_matrix.delete_char_set("default", db=self.db), 0)

    def test_add_chars_35(self) -> None:
        self._build("q", char_set="symbols")
        rebuilt = char_sub_matrix.rebuild(
            "qr", "symbols", fonts=self.fonts, db=self.db, progress=False
        )
        self.assertEqual(rebuilt, ["q", "r"])
        self.assertEqual(
            set(char_sub_matrix.get("symbols", db=self.db)), {"qq", "qr", "rr"}
        )

    # --------------------------------------------------------------- missing_chars
    def test_missing_chars_36(self) -> None:
        self.assertEqual(char_sub_matrix.missing_chars("a b\n", db=self.db), [])
        self.assertEqual(
            char_sub_matrix.missing_chars("aXyé", db=self.db), ["X", "y", "é"]
        )
        self.assertEqual(char_sub_matrix.missing_chars("aaz", db=self.db), ["z"])

    def test_missing_chars_37(self) -> None:
        self.assertEqual(char_sub_matrix.missing_chars("a", "nope", db=self.db), ["a"])

    def test_missing_chars_38(self) -> None:
        with self.assertRaisesRegex(
            char_sub_matrix.CharSubMatrixError, "substitution matrix"
        ):
            char_sub_matrix.missing_chars(
                "a", db=Path(self.tmp.name) / "nothing.sqlite"
            )
        with self.assertRaisesRegex(
            char_sub_matrix.CharSubMatrixError, "no characters"
        ):
            char_sub_matrix.get("nope", db=self.db)
        with self.assertRaisesRegex(
            char_sub_matrix.CharSubMatrixError, "substitution matrix"
        ):
            char_sub_matrix.get(db=Path(self.tmp.name) / "nothing.sqlite")

    # ----------------------------------------------------------- the shipped matrix
    def test_shipped_matrix_39(self) -> None:
        subs = char_sub_matrix.get()
        chars = char_sub_matrix.list_chars()
        self.assertEqual(len(chars), len(char_sub_matrix.CHARS))
        self.assertEqual(len(subs), len(chars) * (len(chars) + 1) // 2)
        self.assertEqual(subs["aa"], char_sub_matrix.IDENTICAL_SUB)
        self.assertNotIn("ba", subs)

    def test_shipped_matrix_40(self) -> None:
        # The characters that used to make a run fail are all in there now.
        chars = set(char_sub_matrix.list_chars())
        for char in "–µÅÇ±²·…éø\nt \t":
            self.assertIn(char, chars, repr(char))

    def test_shipped_matrix_41(self) -> None:
        ratios = char_sub_matrix.get_ratios()
        self.assertGreater(ratios[("O", "Q")], 0.65)  # lookalikes score high
        self.assertGreater(ratios[("e", "é")], 0.65)
        self.assertLess(ratios[("X", "a")], 0.30)  # unlike shapes score low
        self.assertEqual(ratios[(" ", "a")], 0.0)  # blank against ink is no match
        self.assertEqual(ratios[("\n", " ")], 1.0)  # blank against blank is a match
        self.assertEqual(char_sub_matrix.get()[("\n ")], char_sub_matrix.IDENTICAL_SUB)


if __name__ == "__main__":
    unittest.main()
