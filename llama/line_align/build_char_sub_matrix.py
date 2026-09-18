#!/usr/bin/env python3
"""
Build or update the character substitution matrix.

The matrix is what lets the line aligner treat "O" and "Q" as a small
substitution and "a" and "X" as a big one. Characters are rendered in a handful
of fonts, their pixels are slid over one another, and the best overlap becomes a
coarse substitution value. See llama/line_align/char_sub_matrix.py for the
details.

Adding characters, or adding fonts, only measures what is not already measured,
so it is safe to run this repeatedly:

    build_char_sub_matrix.py                      # the default character set
    build_char_sub_matrix.py --chars "ÆØ♂"        # add a few characters
    build_char_sub_matrix.py --add-font my.ttf    # rescore everything in a new font
"""

import argparse
import logging
import textwrap

from llama.line_align import char_sub_matrix as matrix
from llama.pylib import log


def main(args: argparse.Namespace) -> None:
    log.started(args=args)

    if args.list_sets:
        _show_sets()
    elif args.list_chars:
        _show_chars(args)
    elif args.check_chars:
        _check_chars(args)
    else:
        _add_chars(args)

    log.finished()


def _add_chars(args: argparse.Namespace) -> None:
    fonts = [*matrix.FONTS, args.add_font] if args.add_font else matrix.FONTS
    add = matrix.rebuild if args.rebuild else matrix.add_chars
    chars = add(
        args.chars,
        args.char_set,
        fonts=fonts,
        font_size=args.font_size,
        canvas=args.canvas,
        threshold=args.threshold,
        force=args.force,
    )
    logging.info("Character set %s has %d characters", args.char_set, len(chars))


def _show_sets() -> None:
    """Report the character sets that are already measured."""
    sets = matrix.list_char_sets()
    if not sets:
        logging.warning(
            "The matrix is empty, run this script without options to build it"
        )
        return
    for name in sets:
        info = matrix.build_info(name) or {}
        logging.info(
            "%s: %d characters, %d fonts, last built %s",
            name,
            len(matrix.list_chars(name)),
            str(info.get("fonts", "")).count("\n") + 1,
            info.get("updated", "never"),
        )


def _show_chars(args: argparse.Namespace) -> None:
    chars = matrix.list_chars(args.char_set)
    if not chars:
        logging.warning("Character set %s is empty", args.char_set)
        return
    logging.info("Character set %s:", args.char_set)
    print("".join(chars))


def _check_chars(args: argparse.Namespace) -> None:
    missing = matrix.missing_chars(args.check_chars, args.char_set)
    if missing:
        logging.warning("%d characters are not in %s", len(missing), args.char_set)
        print("".join(missing))
    else:
        logging.info("All of those characters are in %s", args.char_set)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(main.__doc__ or ""),
    )

    arg_parser.add_argument(
        "--char-set",
        default=matrix.DEFAULT_CHAR_SET,
        metavar="NAME",
        help="""The character set to work on. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--chars",
        default=matrix.CHARS,
        metavar="CHARS",
        help="""Every character in this string is added to the character set, then
            each pair of characters in the set is measured. The default is the
            built in character set of OCRed specimen labels, which includes a
            space, a tab and a newline. (default: char_sub_matrix.CHARS)""",
    )

    arg_parser.add_argument(
        "--add-font",
        metavar="PATH",
        help="""A TrueType or OpenType font file to measure with on top of the fonts
            the character set already uses. (default: none)""",
    )

    arg_parser.add_argument(
        "--font-size",
        type=int,
        default=matrix.DEFAULT_FONT_SIZE,
        metavar="PIXELS",
        help="""The size glyphs are rendered at. Changing this invalidates an
            existing character set, pass --force to change it anyway.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--canvas",
        type=int,
        default=matrix.DEFAULT_CANVAS,
        metavar="PIXELS",
        help="""The size of the square image that holds one rendered character. Must
            be big enough for the widest character at --font-size. (default:
            %(default)s)""",
    )

    arg_parser.add_argument(
        "--threshold",
        type=int,
        default=matrix.DEFAULT_THRESHOLD,
        metavar="LEVEL",
        help="""Anti aliased pixels this bright or brighter count as ink. (default:
            %(default)s)""",
    )

    arg_parser.add_argument(
        "--rebuild",
        action="store_true",
        help="""Throw the character set away and measure it again instead of only
            measuring what is missing.""",
    )

    arg_parser.add_argument(
        "--force",
        action="store_true",
        help="""Measure with the given rendering settings even though the character
            set was measured with different ones.""",
    )

    arg_parser.add_argument(
        "--list-sets",
        action="store_true",
        help="List the character sets in the matrix and exit.",
    )

    arg_parser.add_argument(
        "--list-chars",
        action="store_true",
        help="Print the characters of --char-set and exit.",
    )

    arg_parser.add_argument(
        "--check-chars",
        metavar="CHARS",
        help="""Print which of these characters are missing from --char-set and exit.
            Alignment fails on characters the matrix does not know, so a job can
            check its input with this first.""",
    )

    return arg_parser.parse_args()


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
