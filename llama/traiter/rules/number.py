import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from spacy import Language, registry
from spacy.tokens import Span

from llama.traiter.pipes import add
from llama.traiter.pylib import term_util
from llama.traiter.pylib.pattern_compiler import Compiler
from llama.traiter.pylib.util import to_positive_float as as_float
from llama.traiter.rules.base_rule import BaseRule

FLOAT_RE: str = r"\d{1,4}(\.\d{,3})?"
FLOAT3_RE: str = r"(\d*[,])?\d{3}(\.\d{,3})?"
DEC_RE: str = r"\.\d{1,3}"

FACT_LEN = 2

# This pipe is used multiple times
UNIQUE = 0  # A tiebreaker used to rename the Number pipe


@dataclass(eq=False)
class Number(BaseRule):
    # Class vars ----------
    enable_pipes: ClassVar[list[str]] = []

    csv: ClassVar[Path] = Path(__file__).parent / "terms" / "number_word_terms.csv"
    replace: ClassVar[dict[str, str]] = term_util.look_up_table(csv, "replace", int)
    # ---------------------

    number: float | None = None
    is_fraction: bool | None = None
    is_word: bool | None = None
    is_int: bool | None = None

    @classmethod
    def pipe(cls, nlp: Language, _overwrite: list[str] | None = None) -> None:
        global UNIQUE
        UNIQUE += 1

        term_pipes = add.term_pipe(nlp, name=f"number_terms_{UNIQUE}", path=cls.csv)
        cls.enable_pipes.extend(term_pipes)

        word_pipe = f"number_word_{UNIQUE}"
        add.trait_pipe(nlp, name=word_pipe, compiler=cls.number_word_patterns())
        cls.enable_pipes.append(word_pipe)

        number_pipe = f"number_{UNIQUE}"
        add.trait_pipe(nlp, name=number_pipe, compiler=cls.number_patterns())
        cls.enable_pipes.append(number_pipe)

        cleanup_pipe = f"number_cleanup_{UNIQUE}"
        add.cleanup_pipe(nlp, name=cleanup_pipe)
        cls.enable_pipes.append(cleanup_pipe)

    @classmethod
    def number_patterns(cls) -> list[Compiler]:
        decoder = {
            "99.0": {"LOWER": {"REGEX": f"^{FLOAT_RE}+$"}},
            "999.0": {"LOWER": {"REGEX": f"^{FLOAT3_RE}+$"}},
            ".99": {"LOWER": {"REGEX": f"^{DEC_RE}+$"}},
        }
        return [
            Compiler(
                label="number",
                on_match="number_match",
                decoder=decoder,
                patterns=[
                    " 99.0 ",
                    " 999.0 ",
                    " .99 ",
                ],
            ),
        ]

    @classmethod
    def number_word_patterns(cls) -> list[Compiler]:
        decoder = {
            "word": {"ENT_TYPE": "number_word"},
        }
        return [
            Compiler(
                label="number",
                on_match="number_word_match",
                decoder=decoder,
                patterns=[
                    " word ",
                ],
            ),
        ]

    @classmethod
    def number_match(cls, ent: Span) -> "Number":
        number = as_float(ent.text)
        is_int = re.search(r"[.]", ent.text) is None
        trait = cls.from_ent(ent, number=number, is_int=is_int)
        return trait

    @classmethod
    def number_word_match(cls, ent: Span) -> "Number":
        word = ent.text.lower()
        number = cls.replace.get(word)

        trait = cls.from_ent(ent, number=number, is_word=True)

        return trait


@registry.misc("number_match")
def number_match(ent: Span) -> Number:
    return Number.number_match(ent)


@registry.misc("number_word_match")
def number_word_match(ent: Span) -> Number:
    return Number.number_word_match(ent)
