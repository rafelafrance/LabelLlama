import json
import random
from pathlib import Path

import dspy
import Levenshtein

from .darwin_core import DWC

PROMPT = """
    From the label get the scientific name, scientific name authority, family taxon,
    collection date, elevation, latitude and longitude, Township Range Section (TRS),
    Universal Transverse Mercator (UTM), administrative unit, locality, habitat
    collector names, collector ID, determiner names, determiner ID, specimen ID number,
    associated taxa, and any other observations.
    If it is not mentioned return an empty value.
    """


class InfoExtractor(dspy.Signature):
    """Analyze herbarium specimen labels and extract this information."""

    # Input fields
    text: str = dspy.InputField(default="", desc="Herbarium label text")
    prompt: str = dspy.InputField(default="", desc="Extract these traits")

    # Output traits -- Just capturing the text for now
    dwc_scientific_name: list[str] = dspy.OutputField(
        default=[], desc="Scientific name", alias="dwc:scientificName"
    )
    dwc_scientific_name_authority: list[str] = dspy.OutputField(
        default=[],
        desc="Scientific name authority",
        alias="dwc:scientificNameAuthority",
    )
    dwc_family: list[str] = dspy.OutputField(
        default=[], desc="Taxonomic family", alias="dwc:family"
    )
    dwc_verbatim_event_date: list[str] = dspy.OutputField(
        default=[], desc="Specimen collection date", alias="dwc:verbatimEventDate"
    )
    dwc_verbatim_locality: list[str] = dspy.OutputField(
        default=[], desc="Collected from this locality", alias="dwc:verbatimLocality"
    )
    dwc_habitat: list[str] = dspy.OutputField(
        default=[], desc="Collected from this habitat", alias="dwc:habitat"
    )
    dwc_verbatim_elevation: list[str] = dspy.OutputField(
        default=[], desc="Specimen elevation", alias="dwc:verbatimElevation"
    )
    dwc_verbatim_coordinates: list[str] = dspy.OutputField(
        default=[], desc="Latitude and longitude", alias="dwc:verbatimCoordinates"
    )
    dwc_recorded_by: list[str] = dspy.OutputField(
        default=[], desc="Collector names", alias="dwc:recordedBy"
    )
    dwc_recorded_by_id: list[str] = dspy.OutputField(
        default=[], desc="Collector ID", alias="dwc:recordedByID"
    )
    dwc_identified_by: list[str] = dspy.OutputField(
        default=[], desc="Determiners names", alias="dwc:identifiedBy"
    )
    dwc_identified_by_id: list[str] = dspy.OutputField(
        default=[], desc="Determiner ID", alias="dwc:identifiedByID"
    )
    dwc_occurrence_id: list[str] = dspy.OutputField(
        default=[], desc="Specimen ID", alias="dwc:occurrenceID"
    )
    dwc_associated_taxa: list[str] = dspy.OutputField(
        default=[], desc="Associated taxa", alias="dwc:associatedTaxa"
    )
    dwc_occurrence_remarks: list[str] = dspy.OutputField(
        default=[], desc="Other observations", alias="dwc:occurrenceRemarks"
    )
    verbatim_administrative_unit: list[str] = dspy.OutputField(
        default=[], desc="Administrative units", alias="verbatimAdministrativeUnit"
    )
    verbatim_trs: list[str] = dspy.OutputField(
        default=[], desc="Township Range Section (TRS)", alias="verbatimTRS"
    )
    verbatim_utm: list[str] = dspy.OutputField(
        default=[], desc="Universal Transverse Mercator (UTM)", alias="verbatimUTM"
    )


INPUT_FIELDS = ("text", "prompt")
OUTPUT_FIELDS = [t for t in vars(InfoExtractor()) if t not in INPUT_FIELDS]


def dict2example(dct: dict[str, str]) -> dspy.Example:
    example = dspy.Example(text=dct["text"], prompt=PROMPT).with_inputs(
        "text", "prompt"
    )
    for fld in OUTPUT_FIELDS:
        setattr(example, fld, dct["annotations"][DWC[fld]])
    return example


def read_label_data(label_json: Path, limit: int = 0) -> list[dict]:
    with label_json.open() as f:
        label_data = json.load(f)
        # label_data = [json.loads(ln) for ln in f]
        label_data = label_data[:limit] if limit else label_data
    return label_data


def split_examples(examples: list[dspy.Example], train_split: float, val_split: float):
    random.shuffle(examples)

    total = len(examples)
    split1 = round(total * train_split)
    split2 = split1 + round(total * val_split)

    train_set = examples[:split1]
    val_set = examples[split1:split2]
    test_set = examples[split2:]

    return train_set, val_set, test_set


def levenshtein_score(example: dspy.Example, prediction: dspy.Prediction, _trace=None):
    """Score predictions from DSPy."""
    total_score: float = 0.0

    for fld in OUTPUT_FIELDS:
        true = getattr(example, fld)
        pred = getattr(prediction, fld)

        value = Levenshtein.ratio(true, pred)
        total_score += value

    total_score /= len(OUTPUT_FIELDS)
    return total_score
