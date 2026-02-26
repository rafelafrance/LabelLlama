from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from spacy.language import Language

from llama.traiter.pipes import cleanup, context, debug, phrase, trait
from llama.traiter.pylib import term_util
from llama.traiter.pylib.pattern_compiler import ACCUMULATOR, Compiler


def term_pipe(
    nlp: Language,
    *,
    name: str,
    path: Path | list[Path],
) -> list[str]:
    paths = path if isinstance(path, Iterable) else [path]

    # Gather terms and make sure they have the needed fields
    by_attr = defaultdict(list)
    replaces = defaultdict(dict)

    for path_ in paths:
        terms = term_util.read_terms(path_)
        for term in terms:
            label = term.get("label")
            pattern = {"label": label, "pattern": term["pattern"]}
            attr = term.get("attr", "lower").upper()
            by_attr[attr].append(pattern)
            if replace := term.get("replace"):
                replaces[attr][term["pattern"]] = replace

    # Add a pipe for each phrase matcher attribute
    names = []
    with nlp.select_pipes(enable="tokenizer"):
        for attr, patterns in by_attr.items():
            name = f"{name}_{attr.lower()}"
            names.append(name)
            config = {
                "patterns": patterns,
                "attr": attr,
            }
            nlp.add_pipe(phrase.PHRASE_PIPE, name=name, config=config)

    return names


def trait_pipe(
    nlp: Language,
    *,
    name: str,
    compiler: list[Compiler] | Compiler,
    overwrite: list[str] | None = None,
) -> None:
    compilers = compiler if isinstance(compiler, Iterable) else [compiler]
    patterns = defaultdict(list)
    dispatch = {}

    for compiler_ in compilers:
        compiler_.compile()
        patterns[compiler_.label] += compiler_.patterns

        if compiler_.on_match:
            dispatch[compiler_.label] = compiler_.on_match

    config = {
        "patterns": patterns,
        "dispatch": dispatch,
        "keep": ACCUMULATOR.keep,
        "overwrite": overwrite,
    }
    nlp.add_pipe(trait.ADD_TRAITS, name=name, config=config)


def context_pipe(
    nlp: Language,
    *,
    name: str,
    compiler: list[Compiler] | Compiler,
    overwrite: list[str] | None = None,
) -> None:
    compilers = compiler if isinstance(compiler, Iterable) else [compiler]
    patterns = defaultdict(list)
    dispatch = {}

    for compiler_ in compilers:
        compiler_.compile()
        patterns[compiler_.label] += compiler_.patterns

        if compiler_.on_match:
            dispatch[compiler_.label] = compiler_.on_match

    config = {
        "patterns": patterns,
        "dispatch": dispatch,
        "overwrite": overwrite,
    }
    nlp.add_pipe(context.CONTEXT_TRAITS, name=name, config=config)


def cleanup_pipe(nlp: Language, *, name: str) -> None:
    config = {"keep": ACCUMULATOR.keep}
    nlp.add_pipe(cleanup.CLEANUP_TRAITS, name=name, config=config)


def debug_tokens(nlp: Language) -> None:
    debug.tokens(nlp)


def debug_ents(nlp: Language) -> None:
    debug.ents(nlp)


def custom_pipe(
    nlp: Language,
    registered: str,
    name: str = "",
    config: dict | None = None,
) -> None:
    config = config or {}
    name = name or registered
    nlp.add_pipe(registered, name=name, config=config)
