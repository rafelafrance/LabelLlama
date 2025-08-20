import dspy

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
    "dwc_country": "dwc:country",
    "dwc_state_province": "dwc:stateProvince",
    "dwc_county": "dwc:county",
    "dwc_occurrence_remarks": "dwc:occurrenceRemarks",
    "verbatim_trs": "verbatimTRS",
    "verbatim_utm": "verbatimUTM",
}

PROMPT = """
    From the label get the scientific name, scientific name authority, family taxon,
    collection date, elevation, latitude and longitude, Township Range Section (TRS),
    Universal Transverse Mercator (UTM), administrative unit, locality, habitat
    collector names, collector ID, determiner names, determiner ID, specimen ID number,
    associated taxa, and any other observations.
    If it is not mentioned return an empty value.
    """


class LightningBugLabel(dspy.Signature):
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
    dwc_country: list[str] = dspy.OutputField(
        default=[],
        desc="The country where the specimen was collected",
        alias="dwc:country",
    )
    dwc_state_province: list[str] = dspy.OutputField(
        default=[],
        desc="The state or province where the specimen was collected",
        alias="dwc:stateProvince",
    )
    dwc_county: list[str] = dspy.OutputField(
        default=[],
        desc="The county where the specimen was collected",
        alias="dwc:county",
    )
    dwc_occurrence_remarks: list[str] = dspy.OutputField(
        default=[], desc="Other observations", alias="dwc:occurrenceRemarks"
    )
    verbatim_trs: list[str] = dspy.OutputField(
        default=[], desc="Township Range Section (TRS)", alias="verbatimTRS"
    )
    verbatim_utm: list[str] = dspy.OutputField(
        default=[], desc="Universal Transverse Mercator (UTM)", alias="verbatimUTM"
    )


INPUT_FIELDS = ("text", "prompt")
OUTPUT_FIELDS = [t for t in vars(LightningBugLabel()) if t not in INPUT_FIELDS]
