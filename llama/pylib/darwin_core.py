from typing import Any

from llama.label_types.herbarium_label import DWC


def to_dwc(label: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a label as a JSON dict into a Darwin Core labeled dict.

    The label is coming from the JSON lines output of the OCR engine.
    # TODO: Convert occurrenceRemarks to dynamicProperties after processing
    """
    dwc = {}
    for key, val in label.items():
        if key in DWC:
            key = DWC.get(key, key)
            if key == "dwc:occurrenceRemarks":
                dwc[key] = format_text_as_html(val)
            elif key.startswith("dwc:"):
                dwc[key] = format_text_as_html(val)
            else:
                dwc["dwc:dynamicProperties"][key] = format_text_as_html(val)
    return dwc


def rekey(label: dict[str, Any]) -> dict[str, Any]:
    return {DWC[k]: v for k, v in label.items()}


def format_text_as_html(text: Any) -> str:
    if not isinstance(text, str):
        return text
    text = text.replace("\n", "<br/>")
    return text
