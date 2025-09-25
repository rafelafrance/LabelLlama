import dspy

DWC = {
    "dwc_scientific_name": "dwc:scientificName",
    "dwc_scientific_name_authority": "dwc:scientificNameAuthority",
    "dwc_family": "dwc:family",
    "dwc_genus": "dwc:genus",
    "dwc_subgenus": "dwc:subgenus",
    "dwc_specific_epithet": "dwc:specificEpithet",
    "dwc_verbatim_event_date": "dwc:verbatimEventDate",
    "dwc_verbatim_locality": "dwc:verbatimLocality",
    "dwc_habitat": "dwc:habitat",
    "dwc_sex": "dwc:sex",
    "dwc_verbatim_elevation": "dwc:verbatimElevation",
    "dwc_verbatim_coordinates": "dwc:verbatimCoordinates",
    "dwc_recorded_by": "dwc:recordedBy",
    "dwc_recorded_by_id": "dwc:recordedByID",
    "dwc_identified_by": "dwc:identifiedBy",
    "dwc_identified_by_id": "dwc:identifiedByID",
    "dwc_occurrence_id": "dwc:occurrenceID",
    "dwc_country": "dwc:country",
    "dwc_state_province": "dwc:stateProvince",
    "dwc_county": "dwc:county",
    "dwc_occurrence_remarks": "dwc:occurrenceRemarks",
}

PROMPT = """
    From the label get the scientific name, scientific name authority, family,
    genus, subgenus, specificEpithet,
    collection date, elevation, latitude and longitude, locality, habitat, sex,
    collection country, collection state or province, collection county,
    collector names, collector ID, determiner names, determiner ID, specimen ID number,
    and any other observations.
    If it is not mentioned return an empty value. Do not hallucinate.
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
    dwc_genus: list[str] = dspy.OutputField(
        default=[], desc="Taxonomic genus", alias="dwc:genus"
    )
    dwc_subgenus: list[str] = dspy.OutputField(
        default=[], desc="Taxonomic subgenus", alias="dwc:subgenus"
    )
    dwc_specific_epithet: list[str] = dspy.OutputField(
        default=[], desc="Taxonomic specific epithet", alias="dwc:specificEpithet"
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
    dwc_sex: list[str] = dspy.OutputField(
        default=[], desc="Sex of the specimen", alias="dwc:sex"
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


INPUT_FIELDS = ("text", "prompt")
OUTPUT_FIELDS = [t for t in vars(LightningBugLabel()) if t not in INPUT_FIELDS]
