from collections import defaultdict
from typing import Any

DWC = {
    "dwc_scientific_name": "dwc:scientificName",
    "dwc_scientific_name_authority": "dwc:scientificNameAuthority",
    "dwc_family": "dwc:family",
    "dwc_verbatim_event_date": "dwc:verbatimEventDate",
    "dwc_verbatim_locality": "dwc:verbatimLocality",
    "dwc_habitat": "dwc:habitat",
    "dwc_verbatim_elevation": "dwc:verbatimElevation",
    "dwc_verbatim_coordinates": "dwc:verbatimCoordinates",
    "dwc_recorded_by": "dwc:recordedBy",
    "dwc_recorded_by_id": "dwc:recordedByID",
    "dwc_identified_by": "dwc:identifiedBy",
    "dwc_identified_by_id": "dwc:identifiedByID",
    "dwc_occurrence_id": "dwc:occurrenceID",
    "dwc_associated_taxa": "dwc:associatedTaxa",
    "dwc_occurrence_remarks": "dwc:occurrenceRemarks",
    "verbatim_administrative_unit": "verbatimAdministrativeUnit",
    "verbatim_trs": "verbatimTRS",
    "verbatim_utm": "verbatimUTM",
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
