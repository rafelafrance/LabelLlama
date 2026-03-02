from dspy import InputField, OutputField, Signature


class HerbariumSheet(Signature):
    """Analyze text from a herbarium sheets and extract information."""

    text: str = InputField()

    scientific_name: list[str] = OutputField(
        default=[],
        desc="Scientific name or species",
        alias="dwc:scientificName",
    )
    scientific_name_authority: list[str] = OutputField(
        default=[],
        desc="Scientific name authority",
        alias="dwc:scientificNameAuthority",
    )
    family: list[str] = OutputField(
        default=[],
        desc="Taxonomic family",
        alias="dwc:family",
    )
    associated_taxa: list[str] = OutputField(
        default=[],
        desc="Was the specimen found near, around, or on another species",
        alias="dwc:associatedTaxa",
    )
    occurrence_id: list[str] = OutputField(
        default=[],
        desc="The numbers used to identify the specimen",
        alias="dwc:occurrenceID",
    )
    event_date: list[str] = OutputField(
        default=[],
        desc="When was the specimen collected",
        alias="dwc:eventDate",
    )
    recorded_by: list[str] = OutputField(
        default=[],
        desc="The person or people who collected the specimen",
        alias="dwc:recordedBy",
    )
    recorded_by_id: list[str] = OutputField(
        default=[],
        desc="What ID did the collector(s) use to identify themself",
        alias="dwc:recordedByID",
    )
    identified_by: list[str] = OutputField(
        default=[],
        desc="Who identified or verified the species",
        alias="dwc:identifiedBy",
    )
    identified_by_id: list[str] = OutputField(
        default=[],
        desc="The ID did the determiner(s) used to identify themself",
        alias="dwc:identifiedByID",
    )
    elevation: list[str] = OutputField(
        default=[],
        desc="The specimen was collected at this elevation or altitude",
        alias="dwc:elevation",
    )
    coordinates: list[str] = OutputField(
        default=[],
        desc="The specimen was collected at this latitude and longitude",
        alias="dwc:coordinates",
    )
    country: list[str] = OutputField(
        default=[],
        desc="The country where the specimen was collected",
        alias="dwc:country",
    )
    state_province: list[str] = OutputField(
        default=[],
        desc="The state or province where the specimen was collected",
        alias="dwc:stateProvince",
    )
    county: list[str] = OutputField(
        default=[],
        desc="The county where the specimen was collected",
        alias="dwc:county",
    )
    municipality: list[str] = OutputField(
        default=[],
        desc="Collected from this municipality",
        alias="dwc:municipality",
    )
    occurrence_remarks: list[str] = OutputField(
        default=[],
        desc="This contains all other observations",
        alias="dwc:occurrenceRemarks",
    )
    trs: list[str] = OutputField(
        default=[],
        desc=(
            "Township Range Section (TRS), "
            'Examples "T8N R17W", "T4S R3E Sec 27", "T3N R7W SW/4 section 20", '
            '"S.14, T12S, R4W"'
        ),
        alias="TRS",
    )
    utm: list[str] = OutputField(
        default=[],
        desc=(
            "Universal Transverse Mercator (UTM)"
            'Examples  "33T 500000 4649776", "Z12 N7874900 E768500", '
            '"11S 316745.14 3542301.90"'
        ),
        alias="UTM",
    )
    locality: list[str] = OutputField(
        default=[],
        desc="A description of where the specimen was collected",
        alias="dwc:locality",
    )
    habitat: list[str] = OutputField(
        default=[],
        desc="Collected from this habitat, or environment",
        alias="dwc:habitat",
    )
    flowers_present: list[str] = OutputField(
        default=[],
        desc="Are there flowers on the plant?",
        alias="dwc:dynamicProperties:flowers_present",
    )
    fruit_present: list[str] = OutputField(
        default=[],
        desc="Is there fruit on the plant?",
        alias="dwc:dynamicProperties:fruit_present",
    )
    flower_color: list[str] = OutputField(
        default=[],
        desc="What are the colors of the flowers?",
        alias="dwc:dynamicProperties:flower_color",
    )
    fruit_color: list[str] = OutputField(
        default=[],
        desc="What are the colors of the fruits?",
        alias="dwc:dynamicProperties:fruit_color",
    )
    height: list[str] = OutputField(
        default=[],
        desc="How tall is the specimen?",
        alias="dwc:dynamicProperties:plant_height",
    )
    size: list[str] = OutputField(
        default=[],
        desc="Other specimen sizes?",
        alias="dwc:dynamicProperties:plant_size",
    )
    habit: list[str] = OutputField(
        default=[],
        desc="What is the specimen habit? Examples herbaceous, woody, decumbent, erect",
        alias="dwc:dynamicProperties:plant_habit",
    )
    abundance: list[str] = OutputField(
        default=[],
        desc="How common is the specimen? Examples include common, scattered, rare",
        alias="dwc:dynamicProperties:plant_abundance",
    )
    leaf_shape: list[str] = OutputField(
        default=[],
        desc=(
            "What is the shape of the specimen's leaf? "
            "Examples acute, caudate, elliptic, lobed"
        ),
        alias="dwc:dynamicProperties:leaf_shape",
    )
    leaf_margin: list[str] = OutputField(
        default=[],
        desc=(
            "Description of the specimen's leaf margins. "
            "Examples entire, crenate, dentate, serrate"
        ),
        alias="dwc:dynamicProperties:leaf_margin",
    )
