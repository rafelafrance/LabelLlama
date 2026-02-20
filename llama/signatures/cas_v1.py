from dspy import InputField, OutputField, Signature


class CasV1(Signature):
    """Analyze text from herbarium sheets and extract this information."""

    text: str = InputField()

    scientificName: list[str] = OutputField(
        default=[],
        desc="Scientific name or species",
    )
    scientificNameAuthorship: list[str] = OutputField(
        default=[],
        desc="Scientific name authorship (authority)",
    )
    infraspecificEpithet: list[str] = OutputField(
        default=[],
        desc="Contains the subspecies or variety portion of the scientific name",
    )
    infraspecificNameAuthorship: list[str] = OutputField(
        default=[],
        desc="The author (authority) who coined the infraspecific name.",
    )
    family: list[str] = OutputField(
        default=[],
        desc="Taxonomic family",
    )
    associatedTaxa: list[str] = OutputField(
        default=[],
        desc="Was the specimen found near, around, or on another species",
    )
    recordNumber: list[str] = OutputField(
        default=[],
        desc="The number used to identify the specimen",
    )
    recordedBy: list[str] = OutputField(
        default=[],
        desc="The person or people who collected the specimen",
    )
    verbatimEventDate: list[str] = OutputField(
        default=[],
        desc="When was the specimen collected",
    )
    identifiedBy: list[str] = OutputField(
        default=[],
        desc="Who identified or verified the species",
    )
    dateIdentified: list[str] = OutputField(
        default=[],
        desc="When was the specimen identified or verified?",
    )
    country: list[str] = OutputField(
        default=[],
        desc="The country where the specimen was collected",
    )
    stateProvince: list[str] = OutputField(
        default=[],
        desc="The state or province where the specimen was collected",
    )
    county: list[str] = OutputField(
        default=[],
        desc="The county where the specimen was collected",
    )
    municipality: list[str] = OutputField(
        default=[],
        desc="Collected from this municipality",
    )
    verbatimElevation: list[str] = OutputField(
        default=[],
        desc="The specimen was collected at this elevation or altitude",
    )
    verbatimLatitude: list[str] = OutputField(
        default=[],
        desc="The specimen was collected at this latitude.",
    )
    verbatimLongitude: list[str] = OutputField(
        default=[],
        desc="The specimen was collected at this longitude.",
    )
    geodeticDatum: list[str] = OutputField(
        default=[],
        desc=(
            "What geodetic datum is the latitude, longitude, TRS, or UTM using "
            'Examples "NAD27", "NAD83", "WGS84"'
        ),
    )
    trs: list[str] = OutputField(
        default=[],
        desc=(
            "Township Range Section (TRS) "
            'Examples "T8N R17W", "T4S R3E Sec 27", "T3N R7W SW/4 section 20", '
            '"S.14, T12S, R4W"'
        ),
    )
    utm: list[str] = OutputField(
        default=[],
        desc=(
            "Universal Transverse Mercator (UTM) "
            'Examples  "33T 500000 4649776", "Z12 N7874900 E768500", '
            '"11S 316745.14 3542301.90"'
        ),
    )
    locality: list[str] = OutputField(
        default=[],
        desc="A description of where the specimen was collected",
    )
    habitat: list[str] = OutputField(
        default=[],
        desc="Collected from this habitat or environment",
    )
    occurrenceRemarks: list[str] = OutputField(
        default=[],
        desc="This contains all other observations",
    )
