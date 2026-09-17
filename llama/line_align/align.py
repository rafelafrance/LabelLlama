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

GAP_CHAR = "⋄"


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
    gap_char: str = GAP_CHAR

    def align(self, lines: list[str]) -> list[str]:
        """
        Create a multiple sequence alignment of a set of similar text fragments.

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
        """  # noqa: RUF002
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
        row, col = rows, cols
        ri, ci = 0, 0  # consumed so far from aligned / from lines[ln]
        new_line = []
        new_aligned = [[] for _ in aligned]

        # Inside a gap run the next move is forced; state tracks that run.
        state = Dir.NONE

        while row or col:
            if state == Dir.NONE:
                state = trace[row, col].dir_
                if state == Dir.NONE:
                    break

            if state == Dir.DIAG:
                for k in range(len(aligned)):
                    new_aligned[k].append(aligned[k][ri])
                new_line.append(lines[ln][ci])
                row -= 1
                col -= 1
                ri += 1
                ci += 1
                state = Dir.NONE

            elif state == Dir.UP:
                for k in range(len(aligned)):
                    new_aligned[k].append(aligned[k][ri])
                new_line.append(self.gap_char)
                row -= 1
                ri += 1
                state = (
                    Dir.UP
                    if row > 0
                    and trace[row + 1, col].up == trace[row, col].up + self.skew
                    else Dir.NONE
                )

            else:  # Dir.LEFT
                for k in range(len(aligned)):
                    new_aligned[k].append(self.gap_char)
                new_line.append(lines[ln][ci])
                col -= 1
                ci += 1
                state = (
                    Dir.LEFT
                    if col > 0
                    and trace[row, col + 1].left == trace[row, col].left + self.skew
                    else Dir.NONE
                )

        new_aligned.append(new_line)
        return new_aligned

    def build_matrix(
        self, aligned: list[list[str]], lines: list[str], ln: int
    ) -> tuple[int, int, npt.NDArray[Trace]]:
        rows = len(aligned[0])
        cols = len(lines[ln])
        rows_p1, cols_p1 = rows + 1, cols + 1

        # trace[row, col] scores the last `row` chars of the aligned sequences
        # against the last `col` chars of lines[ln].
        trace = np.array(
            [[Trace() for _ in range(cols_p1)] for _ in range(rows_p1)],
            dtype=object,
        )

        # Boundary costs: opening a gap of length n costs gap + (n-1) * skew.
        # .up/.left on these cells is what trace_back uses to extend gap runs.
        for row in range(1, rows_p1):
            cost = self.gap + (row - 1) * self.skew
            trace[row, 0] = Trace(val=cost, up=cost, left=cost, dir_=Dir.UP)
        for col in range(1, cols_p1):
            cost = self.gap + (col - 1) * self.skew
            trace[0, col] = Trace(val=cost, up=cost, left=cost, dir_=Dir.LEFT)

        line = lines[ln]
        for row in range(1, rows_p1):
            for col in range(1, cols_p1):
                up_cell = trace[row - 1, col]
                left_cell = trace[row, col - 1]
                cell = trace[row, col]

                cell.up = max(up_cell.up + self.skew, up_cell.val + self.gap)
                cell.left = max(left_cell.left + self.skew, left_cell.val + self.gap)

                # Diagonal: the new character aligns to a whole column, so its
                # cost is the best substitution over the aligned sequences
                # (columns that are already gaps for a given sequence cost nothing).
                ai, li = rows - row, cols - col
                line_char = line[li]
                best_sub = float("-inf")
                for seq in aligned:
                    other = seq[ai]
                    if other == self.gap_char:
                        continue
                    a, b = sorted((other, line_char))  # matrix stores lex-first order
                    value = self.substitutions.get(a + b)
                    if value is None:
                        raise ValueError(
                            f"Missing substitution for character pair {a + b}"
                        )
                    best_sub = max(best_sub, value)
                diag = best_sub + trace[row - 1, col - 1].val

                cell.val = max(diag, cell.up, cell.left)
                cell.dir_ = (
                    Dir.DIAG
                    if cell.val == diag
                    else Dir.UP
                    if cell.val == cell.up
                    else Dir.LEFT
                )
        return cols, rows, trace
