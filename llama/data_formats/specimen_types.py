import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import dspy
import Levenshtein

from llama.data_formats import herbarium_sheet


@dataclass
class LabelType:
    key: str
    prompt: str
    signature: Any  # An object derived from dspy.Signature
    input_fields: list[str]
    output_fields: list[str]
    dwc: dict[str, Any]


def format_prompt(prompt: str) -> str:
    lines = [ln.strip() for ln in prompt.splitlines()]
    prompt = "\n".join(lines)
    return prompt


SPECIMEN_TYPES = {
    "herbarium": LabelType(
        key="herbarium",
        prompt=format_prompt(herbarium_sheet.PROMPT),
        signature=herbarium_sheet.HerbariumSheet,
        input_fields=list(herbarium_sheet.INPUT_FIELDS),
        output_fields=herbarium_sheet.OUTPUT_FIELDS,
        dwc=herbarium_sheet.DWC,
    ),
    # "bug": LabelType(
    #     key="bug",
    #     prompt=format_prompt(bug_label.PROMPT),
    #     signature=bug_label.BugLabel,
    #     input_fields=list(bug_label.INPUT_FIELDS),
    #     output_fields=bug_label.OUTPUT_FIELDS,
    #     dwc=bug_label.DWC,
    # ),
    # "image": LabelType(
    #     key="image",
    #     prompt=format_prompt(image_with_labels.PROMPT),
    #     signature=image_with_labels.ImageWithLabels,
    #     input_fields=list(image_with_labels.INPUT_FIELDS),
    #     output_fields=image_with_labels.OUTPUT_FIELDS,
    #     dwc={},
    # ),
}


def dict2example(dct: dict[str, str], extractor: LabelType) -> dspy.Example:
    example = dspy.Example(text=dct["text"], prompt=extractor.prompt).with_inputs(
        *extractor.input_fields
    )
    for fld in extractor.output_fields:
        setattr(example, fld, dct["annotations"][extractor.dwc[fld]])
    return example


def flatten_dict(dct: dict[str, Any]) -> None:
    for k, v in dct["annotations"].items():
        val = ""
        if len(v) == 0:
            val = ""
        elif len(v) == 1:
            val = v[0]
        else:
            val = v
        dct[k] = val
    del dct["annotations"]


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
