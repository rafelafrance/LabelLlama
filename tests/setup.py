from ccf.pylib import pipeline

PIPELINE = pipeline.build()


def parse(text: str) -> list:
    text = " ".join(text.split())
    doc = PIPELINE(text)

    traits = [e._.trait for e in doc.ents]

    # from pprint import pp
    # pp(traits)

    return traits
