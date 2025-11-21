import dspy

PROMPT = """
    From the text get the following fields:
        - scientific name: The species.
        - scientific name authority: Who described the species.
        - family: What taxonomic family is the species in.
        - collection date: When was the specimen collected.
        - elevation: The specimen was collected at this altitude.
        - locality: A description of where the specimen was collected.
        - habitat: The specimen was collected in this environment.
        - latitude and longitude: Geolocation coordinates of the collection.
        - country: The specimen was collected in this country.
        - state or province: The specimen was collected in this state or province.
        - county: The specimen was collected in this county.
        - municipality: The specimen was collected in this municipality.
        - collector names: Which person or people collected the specimen.
        - collector ID: What ID did the collector use to identify themself.
        - determiner names: Who identified or verified the species.
        - determiner ID: What ID did the determiner use.
        - specimen ID number: What numbers are used to identify this specimen.
        - associated taxa: Was the specimen found near, around, or on another species.
        - Township Range Section (TRS): Examples
            "T8N R17W", "T4S R3E Sec 27", "T3N R7W SW/4 section 20".
        - Universal Transverse Mercator (UTM): Examples
            "33T 500000 4649776", "Z12 N7874900 E768500", "11S 316745.14 3542301.90".
    All other observations go into occurrence remarks.
    If it is not mentioned return an empty value.
    Do not hallucinate.
    """


class HerbariumSheet(dspy.Signature):
    """Analyze text from herbarium sheets and extract this information."""

    # Input fields
    text: str = dspy.InputField(default="", desc="Herbarium sheet text")
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
    dwc_event_date: list[str] = dspy.OutputField(
        default=[], desc="Specimen collection date", alias="dwc:eventDate"
    )
    dwc_locality: list[str] = dspy.OutputField(
        default=[], desc="Collected from this locality", alias="dwc:locality"
    )
    dwc_habitat: list[str] = dspy.OutputField(
        default=[], desc="Collected from this habitat", alias="dwc:habitat"
    )
    dwc_elevation: list[str] = dspy.OutputField(
        default=[], desc="Specimen elevation", alias="dwc:elevation"
    )
    dwc_coordinates: list[str] = dspy.OutputField(
        default=[], desc="Latitude and longitude", alias="dwc:coordinates"
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
    dwc_municipality: list[str] = dspy.OutputField(
        default=[], desc="Collected from this municipality", alias="dwc:municipality"
    )
    dwc_occurrence_remarks: list[str] = dspy.OutputField(
        default=[], desc="Other observations", alias="dwc:occurrenceRemarks"
    )
    trs: list[str] = dspy.OutputField(
        default=[], desc="Township Range Section (TRS)", alias="TRS"
    )
    utm: list[str] = dspy.OutputField(
        default=[], desc="Universal Transverse Mercator (UTM)", alias="UTM"
    )


INPUT_FIELDS = ("text", "prompt")
OUTPUT_FIELDS = [t for t in vars(HerbariumSheet()) if t not in INPUT_FIELDS]
DWC = {
    f[0]: f[1].alias
    for f in HerbariumSheet.model_fields.items()
    if f[0] not in INPUT_FIELDS
}
