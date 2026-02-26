from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from spacy.language import Language
from spacy.tokens import Span
from spacy.util import registry

from llama.traiter.pipes import add
from llama.traiter.pylib import const, term_util
from llama.traiter.pylib.pattern_compiler import Compiler
from llama.traiter.rules.base_rule import BaseRule


@dataclass(eq=False)
class Elevation(BaseRule):
    # Class vars ----------
    enable_pipes: ClassVar[list[str]] = ["elevation_patterns", "elevation_cleanup"]

    float_re: ClassVar[str] = r"^(\d[\d,.]*)$"
    all_units: ClassVar[list[str]] = ["metric_length", "imperial_length"]
    elevation_csv: ClassVar[Path] = (
        Path(__file__).parent / "terms" / "elevation_terms.csv"
    )
    unit_csv: ClassVar[Path] = Path(__file__).parent / "terms" / "unit_length_terms.csv"
    about_csv: ClassVar[Path] = Path(__file__).parent / "terms" / "about_terms.csv"
    numeric_csv: ClassVar[Path] = Path(__file__).parent / "terms" / "numeric_terms.csv"
    tic_csv: ClassVar[Path] = Path(__file__).parent / "terms" / "unit_tic_terms.csv"
    all_csvs: ClassVar[list[Path]] = [
        elevation_csv,
        unit_csv,
        about_csv,
        tic_csv,
        numeric_csv,
    ]

    replace: ClassVar[dict[str, str]] = term_util.look_up_table(all_csvs, "replace")
    factors_cm: ClassVar[dict[str, float]] = term_util.look_up_table(
        (unit_csv, tic_csv),
        "factor_cm",
        float,
    )
    factors_m: ClassVar[dict[str, float]] = {
        k: v / 100.0 for k, v in factors_cm.items()
    }
    # ---------------------

    elevation: float | None = None
    elevation_high: float | None = None
    units: str | None = None
    about: bool | None = None

    @classmethod
    def pipe(cls, nlp: Language) -> None:
        term_pipes = add.term_pipe(nlp, name="elevation_terms", path=cls.all_csvs)
        cls.enable_pipes.extend(term_pipes)

        # add.debug_tokens(nlp)  # ###################################################
        add.trait_pipe(
            nlp,
            name="elevation_patterns",
            compiler=cls.elevation_compilers(),
            overwrite=["number"],
        )
        add.cleanup_pipe(nlp, name="elevation_cleanup")

    @classmethod
    def elevation_compilers(cls) -> list[Compiler]:
        label_ender = r"[:=;,.]"
        return [
            Compiler(
                label="elevation",
                on_match="elevation_match",
                decoder={
                    "(": {"TEXT": {"IN": const.OPEN}},
                    ")": {"TEXT": {"IN": const.CLOSE}},
                    "to": {"ENT_TYPE": "range_term"},
                    "/": {"TEXT": {"IN": const.SLASH}},
                    ",": {"TEXT": {"REGEX": rf"^{label_ender}+$"}},
                    "99": {"ENT_TYPE": "number"},
                    "about": {"ENT_TYPE": "about_term"},
                    "label": {"ENT_TYPE": "elev_label"},
                    "m": {"ENT_TYPE": {"IN": cls.all_units}},
                },
                patterns=[
                    "99 to 99 m*",
                    "99 m* label* (? 99 m* )? about* ",
                    "about* ,* 99 m* (? 99 m* ,? )?",
                    "about* ,* 99 m* / 99 m*",
                    "about* ,* 99 m*",
                ],
            ),
        ]

    @classmethod
    def elevation_match(cls, ent: Span) -> "Elevation":
        values = []
        units_ = ""
        expected_len = 1
        about = None
        hi = None

        for sub_ent in ent.ents:
            # Find numbers
            if sub_ent.label_ == "number":
                values.append(sub_ent._.trait.number)

            # Find units
            elif sub_ent.label_ in cls.all_units and not units_:
                units_ = cls.replace.get(sub_ent.text.lower(), sub_ent.text.lower())

            elif sub_ent.label_ == "about_term":
                about = True

            # If there's a dash it's a range
            elif sub_ent.label_ in "range_term":
                expected_len = 2

        factor = cls.factors_m[units_]

        elevation = round(values[0] * factor, 3)
        units_ = "m"

        # Handle an elevation range
        if expected_len > 1:
            hi = round(values[1] * factor, 3)

        return cls.from_ent(
            ent,
            elevation=elevation,
            elevation_high=hi,
            units=units_,
            about=about,
        )


@registry.misc("elevation_match")
def elevation_match(ent: Span) -> Elevation:
    return Elevation.elevation_match(ent)
