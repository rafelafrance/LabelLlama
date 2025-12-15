"""
Naive implementations of string algorithms based on Gusfield, 1997.

I.e. There's _plenty_ of room for improvement.

NOTE: The functions are geared towards OCR errors and not human
errors. OCR engines will often mistake one letter for another
or drop/add a character (particularly from the ends) but
will seldom transpose characters, which humans do often.

Therefore: I do not consider transpositions in the Needleman Wunsch
distances, and substitutions are based on visual similarity, etc.
"""

from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import numpy.typing as npt

from llama.pylib import const


class Dir(Enum):
    NONE = 0
    DIAG = 1
    LEFT = 2
    UP = 3


@dataclass
class Trace:
    val: float = 0.0
    up: float = 0.0
    left: float = 0.0
    dir_: Dir = Dir.NONE


@dataclass
class LineAlign:
    """
    Multiple sequence alignments of character strings.

    @param substitutions The substitution matrix given as a map, with the key as
        a two character string representing the two character being substituted.
        Symmetry is assumed, so you only need to give the lexically first of a pair,
        i.e. for "ab" and "ba" you only need to send in "ab". The value of the map is
        the cost of substituting the two characters.
    @param gap The gap open penalty for alignments. This is typically negative.
    @param skew The gap extension penalty for the alignments. Also negative.
    @param gap_char The character used to represent gaps in alignment output.
    """

    substitutions: dict[str, float] = field(default_factory=dict)
    gap: float = -3.0
    skew: float = -0.5
    gap_char: str = const.GAP_CHAR

    def align(self, lines: list[str]) -> list[str]:
        """
        Create a multiple sequence alignment of a set of similar short text fragments.

        That is if I am given a set of strings like:
            MOJAVE DESERT, PROVIDENCE MTS.: canyon above
            E. MOJAVE DESERT , PROVIDENCE MTS . : canyon above
            E MOJAVE DESERT PROVTDENCE MTS. # canyon above
            Be ‘MOJAVE DESERT, PROVIDENCE canyon “above

        I should get back something similar to the following. The exact return value
        will depend on the substitution matrix, gap, and skew penalties passed to the
        function.

            ⋄⋄⋄⋄MOJAVE DESERT, PROVIDENCE MTS.: canyon ⋄above
            E.⋄ MOJAVE DESERT, PROVIDENCE MTS.: canyon ⋄above
            E⋄⋄ MOJAVE DESERT⋄ PROVTDENCE MTS.# canyon ⋄above
            Be ‘MOJAVE DESERT, PROVIDENCE ⋄⋄⋄⋄⋄⋄canyon “above

        Where "⋄" characters are used to represent gaps in the alignments.

        @param lines A list of strings to align.
        """
        if len(lines) <= 1:
            return lines

        aligned: list[list[str]] = [list(lines[0])]

        for ln in range(1, len(lines)):
            cols, rows, trace = self.build_matrix(aligned, lines, ln)
            aligned = self.trace_back(aligned, cols, lines, ln, rows, trace)

        result: list[str] = ["".join(a) for a in aligned]
        return result

    def trace_back(
        self,
        aligned: list[list[str]],
        cols: int,
        lines: list[str],
        ln: int,
        rows: int,
        trace: npt.NDArray[Trace],
    ) -> list[list[str]]:
        row = rows
        col = cols
        new_line: list[str] = []

        new_aligned: list[list[str]] = [[] for _ in range(len(aligned))]

        while True:
            cell: Trace = trace[row, col]
            if cell.dir_ == Dir.NONE:
                break

            if cell.dir_ == Dir.DIAG:
                for k in range(len(aligned)):
                    new_aligned[k].append(aligned[k][rows - row])
                new_line.append(lines[ln][cols - col])
                row -= 1
                col -= 1

            elif cell.dir_ == Dir.UP:
                for k in range(len(aligned)):
                    new_aligned[k].append(aligned[k][rows - row])
                new_line.append(self.gap_char)
                row -= 1

            else:
                for k in range(len(aligned)):
                    new_aligned[k].append(self.gap_char)
                new_line.append(lines[ln][cols - col])
                col -= 1
        new_aligned.append(new_line)
        aligned = new_aligned
        return aligned

    def build_matrix(
        self, aligned: list[list[str]], lines: list[str], ln: int
    ) -> tuple[int, int, npt.NDArray[Trace]]:
        rows: int = len(aligned[0])
        cols: int = len(lines[ln])
        rows_p1: int = rows + 1
        cols_p1: int = cols + 1

        items: list[Trace] = [Trace() for _ in range(rows_p1 * cols_p1)]
        trace: npt.NDArray[Trace] = np.array(items, dtype="object")
        trace = trace.reshape((rows_p1, cols_p1))

        # Fill in first row
        penalty: float = self.gap
        for row in range(1, rows_p1):
            trace[row, 0] = Trace(val=penalty, up=penalty, left=penalty, dir_=Dir.UP)
            penalty += self.skew

        # Fill in first column
        penalty = self.gap
        for col in range(1, cols_p1):
            trace[0, col] = Trace(val=penalty, up=penalty, left=penalty, dir_=Dir.LEFT)
            penalty += self.skew

        # Fill in the rest of the matrix
        for row in range(1, rows_p1):
            for col in range(1, cols_p1):
                cell: Trace = trace[row, col]
                cell_up: Trace = trace[row - 1, col]
                cell_left: Trace = trace[row, col - 1]

                cell.up = max(cell_up.up + self.skew, cell_up.val + self.gap)
                cell.left = max(cell_left.left + self.skew, cell_left.val + self.gap)

                diag_val: float = -999_999.0
                for k in range(len(aligned)):
                    aligned_char: str = aligned[k][rows - row]
                    lines_char: str = lines[ln][cols - col]

                    if aligned_char == self.gap_char:
                        continue

                    if aligned_char > lines_char:
                        aligned_char, lines_char = lines_char, aligned_char

                    key = aligned_char + lines_char

                    value: float = self.substitutions.get(key)
                    if value is None:
                        msg: str = (
                            f"One of {key} these characters are missing "
                            "from the substitution matrix."
                        )
                        raise ValueError(msg)

                    diag_val = max(diag_val, value)

                diag_val += trace[row - 1, col - 1].val
                cell.val = max(diag_val, cell.up, cell.left)

                if cell.val == diag_val:
                    cell.dir_ = Dir.DIAG
                else:
                    cell.dir_ = Dir.UP if cell.val == cell.up else Dir.LEFT
        return cols, rows, trace
