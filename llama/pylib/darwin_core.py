from collections import defaultdict
from typing import Any

DWC = {
    "sci_name": "dwc:scientificName",
    "sci_authority": "dwc:scientificNameAuthority",
    "family": "dwc:family",
    "collection_date": "dwc:verbatimEventDate",
    "locality": "dwc:verbatimLocality",
    "habitat": "dwc:habitat",
    "elevation": "dwc:verbatimElevation",
    "lat_long": "dwc:verbatimCoordinates",
    "trs": "verbatimTRS",
    "utm": "verbatimUTM",
    "admin_units": "verbatimAdministrativeUnit",
    "collector_names": "dwc:recordedBy",
    "collector_id": "dwc:recordedByID",
    "determiner_names": "dwc:identifiedBy",
    "determiner_id": "dwc:identifiedByID",
    "id_number": "dwc:occurrenceID",
    "assoc_taxa": "dwc:associatedTaxa",
    "other_obs": "dwc:occurrenceRemarks",
}


def to_dwc(label: dict[str, Any], output_fields: list[str]) -> dict[str, Any]:
    """
    Convert a label as a JSON dict into a Darwin Core labeled dict.

    The label is coming from the JSON lines output of the OCR engine.
    # TODO: Convert occurrenceRemarks to dynamicProperties after processing
    """
    dwc = defaultdict()
    for key, val in label.items():
        if key in output_fields:
            key = DWC.get(key, key)
            if key == "dwc:occurrenceRemarks":
                dwc[key] = format_text_as_html(val)
            elif key.startswith("dwc:"):
                dwc[key] = format_text_as_html(val)
            else:
                dwc["dwc:dynamicProperties"][key] = format_text_as_html(val)
    return dwc


def format_text_as_html(text):
    if not isinstance(text, str):
        return text
    text = text.replace("\n", "<br/>")
    return text
