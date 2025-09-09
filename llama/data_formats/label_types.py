import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, SupportsIndex

import dspy
import Levenshtein

from llama.data_formats import herbarium_label, lightning_bug_label


@dataclass
class LabelType:
    prompt: str
    signature: Any  # An object derived from dspy.Signature
    input_fields: list[str]
    output_fields: list[str]
    dwc: dict[str, SupportsIndex | slice]


LABEL_TYPES = {
    "herbarium": LabelType(
        prompt=herbarium_label.PROMPT,
        signature=herbarium_label.HerbariumLabel,
        input_fields=herbarium_label.INPUT_FIELDS,
        output_fields=herbarium_label.OUTPUT_FIELDS,
        dwc=herbarium_label.DWC,
    ),
    "lightning_bug": LabelType(
        prompt=lightning_bug_label.PROMPT,
        signature=lightning_bug_label.LightningBugLabel,
        input_fields=lightning_bug_label.INPUT_FIELDS,
        output_fields=lightning_bug_label.OUTPUT_FIELDS,
        dwc=lightning_bug_label.DWC,
    ),
}


def dict2example(dct: dict[str, str], extractor: LabelType) -> dspy.Example:
    example = dspy.Example(text=dct["text"], prompt=extractor.prompt).with_inputs(
        *extractor.input_fields
    )
    for fld in extractor.output_fields:
        setattr(example, fld, dct["annotations"][extractor.dwc[fld]])
    return example


def read_label_data(label_json: Path) -> list[dict]:
    with label_json.open() as f:
        label_data = json.load(f)
    return label_data


def split_examples(
    examples: list[dspy.Example], train_split: float, val_split: float
) -> tuple[list[dspy.Example], list[dspy.Example], list[dspy.Example]]:
    random.shuffle(examples)

    total = len(examples)
    split1 = round(total * train_split)
    split2 = split1 + round(total * val_split)

    train_set = examples[:split1]
    val_set = examples[split1:split2]
    test_set = examples[split2:]

    return train_set, val_set, test_set


def levenshtein_score(
    example: dspy.Example, prediction: dspy.Prediction, extractor: LabelType
) -> float:
    """Score predictions from DSPy."""
    total_score: float = 0.0

    for fld in extractor.output_fields:
        true = getattr(example, fld)
        pred = getattr(prediction, fld)

        value = Levenshtein.ratio(true, pred)
        total_score += value

    total_score /= len(extractor.output_fields)
    return total_score
