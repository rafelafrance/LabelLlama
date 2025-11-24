import dspy


class HerbariumSheet(dspy.Signature):
    """Analyze text from a herbarium sheets and extract information."""

    text: str = dspy.InputField()

    scientific_name: list[str] = dspy.OutputField(
        default=[], desc="Scientific name or species", alias="dwc:scientificName",
    )
    scientific_name_authority: list[str] = dspy.OutputField(
        default=[],
        desc="Scientific name authority",
        alias="dwc:scientificNameAuthority",
    )
    family: list[str] = dspy.OutputField(
        default=[], desc="Taxonomic family", alias="dwc:family",
    )
    event_date: list[str] = dspy.OutputField(
        default=[],
        desc="When was the specimen collected",
        alias="dwc:eventDate",
    )
    locality: list[str] = dspy.OutputField(
        default=[],
        desc="A description of where the specimen was collected",
        alias="dwc:locality",
    )
    habitat: list[str] = dspy.OutputField(
        default=[],
        desc="Collected from this habitat, or environment",
        alias="dwc:habitat",
    )
    elevation: list[str] = dspy.OutputField(
        default=[],
        desc="The specimen was collected at this elevation or altitude",
        alias="dwc:elevation",
    )
    coordinates: list[str] = dspy.OutputField(
        default=[],
        desc="The specimen was collected at this latitude and longitude",
        alias="dwc:coordinates",
    )
    recorded_by: list[str] = dspy.OutputField(
        default=[],
        desc="The person or people collected the specimen",
        alias="dwc:recordedBy",
    )
    recorded_by_id: list[str] = dspy.OutputField(
        default=[],
        desc="What ID did the collector use to identify themself",
        alias="dwc:recordedByID",
    )
    identified_by: list[str] = dspy.OutputField(
        default=[], desc="Who identified or verified the species",
        alias="dwc:identifiedBy",
    )
    identified_by_id: list[str] = dspy.OutputField(
        default=[],
        desc="The ID did the determiner used to identify themself",
        alias="dwc:identifiedByID",
    )
    occurrence_id: list[str] = dspy.OutputField(
        default=[],
        desc="The numbers are used to identify this specimen",
        alias="dwc:occurrenceID",
    )
    associated_taxa: list[str] = dspy.OutputField(
        default=[],
        desc="Was the specimen found near, around, or on another species",
        alias="dwc:associatedTaxa",
    )
    country: list[str] = dspy.OutputField(
        default=[],
        desc="The country where the specimen was collected",
        alias="dwc:country",
    )
    state_province: list[str] = dspy.OutputField(
        default=[],
        desc="The state or province where the specimen was collected",
        alias="dwc:stateProvince",
    )
    county: list[str] = dspy.OutputField(
        default=[],
        desc="The county where the specimen was collected",
        alias="dwc:county",
    )
    municipality: list[str] = dspy.OutputField(
        default=[], desc="Collected from this municipality", alias="dwc:municipality",
    )
    occurrence_remarks: list[str] = dspy.OutputField(
        default=[],
        desc="This contains all other observations",
        alias="dwc:occurrenceRemarks",
    )
    trs: list[str] = dspy.OutputField(
        default=[],
        desc=(
            "Township Range Section (TRS), "
            'Examples "T8N R17W", "T4S R3E Sec 27", "T3N R7W SW/4 section 20"'
        ),
        alias="TRS",
    )
    utm: list[str] = dspy.OutputField(
        default=[],
        desc=(
            "Universal Transverse Mercator (UTM)"
            'Examples  "33T 500000 4649776", "Z12 N7874900 E768500", '
            '"11S 316745.14 3542301.90"'
        ),
        alias="UTM",
    )


# INPUT_FIELDS = ("text", )
# OUTPUT_FIELDS = [t for t in vars(HerbariumSheet()) if t not in INPUT_FIELDS]
# DWC = {
#     f[0]: f[1].alias
#     for f in HerbariumSheet.model_fields.items()
#     if f[0] not in INPUT_FIELDS
# }
