from typing import Any


def dwc_format(label: dict[str, Any], dwc: dict[str, str]) -> dict[str, Any]:
    """
    Convert a label as a JSON dict into a Darwin Core labeled dict.

    The label is coming from the JSON lines output of the OCR engine.
    # TODO: Convert occurrenceRemarks to dynamicProperties after processing
    """
    formatted = {}
    for key, val in label.items():
        key = dwc.get(key, "")
        if key == "dwc:occurrenceRemarks":
            formatted[key] = format_text_as_html(val)
        elif key.startswith("dwc:"):
            formatted[key] = format_text_as_html(val)
        elif key:
            formatted["dwc:dynamicProperties"][key] = format_text_as_html(val)
    return formatted


def to_dwc_keys(label: dict[str, Any], dwc: dict[str, str]) -> dict[str, Any]:
    return {dwc[k]: v for k, v in label.items()}


def format_text_as_html(text: Any) -> str:
    if not isinstance(text, str):
        return text
    text = text.replace("\n", "<br/>")
    return text
