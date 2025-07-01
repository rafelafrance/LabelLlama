import random

import dspy
import Levenshtein

PROMPT = """
    What is the scientific name, scientific name authority, family taxon,
    collection date, elevation, latitude and longitude, Township Range Section (TRS),
    Universal Transverse Mercator (UTM), administrative unit, locality, habitat
    collector names, collector ID, determiner names, determiner ID, specimen ID number,
    associated taxa, and any other observations?
    If it is not mentioned return an empty value.
    """


class InfoExtractor(dspy.Signature):
    """Analyze herbarium specimen labels and extract this information."""

    # Input fields
    text: str = dspy.InputField(default="", desc="Herbarium label text")
    prompt: str = dspy.InputField(default="", desc="Extract these traits")

    # Output traits -- Just capturing the text for now
    sci_name: str = dspy.OutputField(default="", desc="Scientific name")
    sci_authority: str = dspy.OutputField(default="", desc="Scientific name authority")
    family: str = dspy.OutputField(default="", desc="Taxonomic family")
    collection_date: str = dspy.OutputField(default="", desc="Specimen collection date")
    locality: str = dspy.OutputField(default="", desc="Collected from this locality")
    habitat: str = dspy.OutputField(default="", desc="Collected from this habitat")
    elevation: str = dspy.OutputField(default="", desc="Specimen elevation")
    lat_long: str = dspy.OutputField(default="", desc="Latitude and longitude")
    trs: str = dspy.OutputField(default="", desc="Township Range Section (TRS)")
    utm: str = dspy.OutputField(default="", desc="Universal Transverse Mercator (UTM)")
    admin_units: list[str] = dspy.OutputField(default="", desc="Administrative units")
    collector_names: list[str] = dspy.OutputField(default="", desc="Collector names")
    collector_id: str = dspy.OutputField(default="", desc="Collector ID")
    determiner_names: list[str] = dspy.OutputField(default="", desc="Determiners names")
    determiner_id: str = dspy.OutputField(default="", desc="Determiner ID")
    id_number: str = dspy.OutputField(default="", desc="Specimen ID")
    assoc_taxa: list[str] = dspy.OutputField(default="", desc="Associated taxa")
    other_obs: list[str] = dspy.OutputField(default="", desc="Other observations")


INPUT_FIELDS = ("text", "prompt")
TRAIT_FIELDS = [t for t in vars(InfoExtractor()) if t not in INPUT_FIELDS]

# Darwin Core garbage is required for output, but it's not helpful elsewhere
DARWIN_CORE = {
    "sci_name": "dwc:scientificName",
    "sci_authority": "dwc:scientificNameAuthority",
    "family": "dwc:family",
    "collection_date": "dwc:verbatimEventDate",
    "locality": "dwc:verbatimLocality",
    "habitat": "dwc:habitat",
    "elevation": "dwc:verbatimElevation",
    "lat_long": "dwc:verbatimCoordinates",
    "trs": "dwc:dynamicProperties:trs",
    "utm": "dwc:dynamicProperties:utm",
    "admin_units": "dwc:dynamicProperties:administrativeUnit",
    "collector_names": "dwc:recordedBy",
    "collector_id": "dwc:recordedByID",
    "determiner_names": "dwc:identifiedBy",
    "determiner_id": "dwc:identifiedByID",
    "id_number": "dwc:occurrenceID",
    "assoc_taxa": "dwc:associatedTaxa",
    "other_obs": "dwc:occurrenceRemarks",
}


def dict2example(dct: dict[str, str]) -> dspy.Example:
    example = dspy.Example(text=dct["text"], prompt=PROMPT).with_inputs(
        "text", "prompt"
    )

    for fld in TRAIT_FIELDS:
        setattr(example, fld, dct[fld])
    return example


# def read_labels(label_jsonl: Path) -> list[dspy.Example]:
#     with label_jsonl.open() as f:
#         label_data = json.load(f)
#     # labels = [dict2example(d) for d in label_data]
#     return label_data


def split_examples(examples: list[dspy.Example], train_split: float, dev_split: float):
    random.shuffle(examples)

    total = len(examples)
    split1 = round(total * train_split)
    split2 = split1 + round(total * dev_split)

    dataset = {
        "train": examples[:split1],
        "dev": examples[split1:split2],
        "test": examples[split2:],
    }

    return dataset


def score_prediction(example: dspy.Example, prediction: dspy.Prediction, trace=None):
    """Score predictions from DSPy."""
    total_score: float = 0.0

    for fld in TRAIT_FIELDS:
        true = getattr(example, fld)
        pred = getattr(prediction, fld)

        value = Levenshtein.ratio(true, pred)
        total_score += value

    total_score /= len(TRAIT_FIELDS)
    return total_score
