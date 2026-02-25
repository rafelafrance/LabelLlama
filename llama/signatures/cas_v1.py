from collections.abc import Callable

from dspy import InputField, OutputField, Signature

from llama.post_process import post_process as post


class CasV1(Signature):
    """
    Analyze text from herbarium sheets and extract this information.

    I need the text exactly as it appears in the text.
    Do not change the text in any way.
    Leave abbreviations exactly as they are.
    If the data field is not found in the text return an empty list.
    Do not add or delete any punctuation and do not add or delete any spaces.
    Do not hallucinate.
    """

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
        desc=(
            "The number used to identify the specimen. The record number is often "
            "found just after the recorded by names.",
        ),
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


CAS_V1_POST: dict[str, Callable[[str, str], str] | None] = {
    "scientificName": post.scientific_name,
    "scientificNameAuthorship": None,
    "infraspecificEpithet": None,
    "infraspecificNameAuthorship": None,
    "family": post.family,
    "associatedTaxa": post.associated_taxa,
    "recordNumber": post.record_number,
    "recordedBy": None,
    "verbatimEventDate": None,
    "identifiedBy": None,
    "dateIdentified": None,
    "country": post.country,
    "stateProvince": post.state_province,
    "county": post.county,
    "municipality": None,
    "verbatimElevation": post.elevation,
    "verbatimLatitude": None,
    "verbatimLongitude": None,
    "geodeticDatum": None,
    "trs": post.trs,
    "utm": post.utm,
    "locality": None,
    "habitat": None,
    "occurrenceRemarks": None,
}
