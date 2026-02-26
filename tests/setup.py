from llama.post_process import pipeline
from llama.traiter.pylib.util import compress

PIPELINE = pipeline.build()


def parse(text: str) -> list:
    text = compress(text)
    doc = PIPELINE(text)

    traits = [e._.trait for e in doc.ents]

    # from pprint import pp
    # pp(traits)

    return traits
