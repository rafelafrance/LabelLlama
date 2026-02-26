import spacy
from spacy.language import Language

from llama.traiter.pipes import extensions, tokenizer
from llama.traiter.rules.elevation import Elevation
from llama.traiter.rules.number import Number

# from llama.traiter.pipes.debug import ents


def build() -> Language:
    extensions.add_extensions()

    nlp = spacy.load("en_core_web_md", exclude=["ner", "tok2vec"])

    tokenizer.setup_tokenizer(nlp)

    Number.pipe(nlp)

    Elevation.pipe(nlp)

    # for pipe_name in nlp.pipe_names:
    #     print(pipe_name)

    return nlp
