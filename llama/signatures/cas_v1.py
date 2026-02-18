from dspy import InputField, OutputField, Signature


class CasV1(Signature):
    """Analyze text from herbarium sheets and extract this information."""

    text: str = InputField()

    scientific_name: list[str] = OutputField(
        default=[],
        desc="Scientific name or species",
        alias="scientificName",
    )
    scientific_name_authorship: list[str] = OutputField(
        default=[],
        desc="The scientific name is according to this authority",
        alias="scientificNameAuthorship",
    )
    infraspecific_epithet: list[str] = OutputField(
        default=[],
        desc="The scientific name of the subspecies or variety",
        alias="infraspecificEpithet",
    )
    infraspecific_name_authorship: list[str] = OutputField(
        default=[],
        desc="The infraspecific name is according to this authority",
        alias="infraspecificNameAuthorship",
    )
    family: list[str] = OutputField(
        default=[],
        desc="Taxonomic family",
        alias="family",
    )
    identified_by: list[str] = OutputField(
        default=[],
        desc="Who identified or verified the specimen",
        alias="identifiedBy",
    )
    date_identified: list[str] = OutputField(
        default=[],
        desc="When was the specimen identified",
        alias="dateIdentified",
    )
    recorded_by: list[str] = OutputField(
        default=[],
        desc="The person or people who collected the specimen",
        alias="recordedBy",
    )
    record_number: list[str] = OutputField(
        default=[],
        desc="The number used to identify the specimen",
        alias="recordNumber",
    )
    verbatim_event_date: list[str] = OutputField(
        default=[],
        desc="When was the specimen collected",
        alias="verbatimEventDate",
    )
    country: list[str] = OutputField(
        default=[],
        desc="The country where the specimen was collected",
        alias="country",
    )
    state_province: list[str] = OutputField(
        default=[],
        desc="The state or province where the specimen was collected",
        alias="stateProvince",
    )
    county: list[str] = OutputField(
        default=[],
        desc="The county where the specimen was collected",
        alias="county",
    )
    municipality: list[str] = OutputField(
        default=[],
        desc="Collected from this municipality",
        alias="municipality",
    )
    locality: list[str] = OutputField(
        default=[],
        desc="A description of where the specimen was collected",
        alias="locality",
    )
    occurrence_remarks: list[str] = OutputField(
        default=[],
        desc="This contains all other observations",
        alias="occurrenceRemarks",
    )
    habitat: list[str] = OutputField(
        default=[],
        desc="Collected from this habitat, or environment",
        alias="habitat",
    )
    associated_taxa: list[str] = OutputField(
        default=[],
        desc="Was the specimen found near, around, or on another species",
        alias="associatedTaxa",
    )
    verbatim_latitude: list[str] = OutputField(
        default=[],
        desc="The specimen was collected at this latitude",
        alias="verbatimLatitude",
    )
    verbatim_longitude: list[str] = OutputField(
        default=[],
        desc="The specimen was collected at this longitude",
        alias="verbatimLongitude",
    )
    geodetic_datum: list[str] = OutputField(
        default=[],
        desc="Locations use this geodetic datum as a reference",
        alias="geodeticDatum",
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
    trs: list[str] = OutputField(
        default=[],
        desc=(
            "Township Range Section (TRS), "
            'Examples "T8N R17W", "T4S R3E Sec 27", "T3N R7W SW/4 section 20", '
            '"S.14, T12S, R4W"'
        ),
        alias="TRS",
    )
    verbatim_elevation: list[str] = OutputField(
        default=[],
        desc="The specimen was collected at this elevation or altitude",
        alias="verbatimElevation",
    )
