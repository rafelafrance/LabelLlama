from dspy import InputField, OutputField, Signature


class CasV1(Signature):
    """
    Analyze text from herbarium sheets and extract this information.

    I need the text exactly as it appears in the text.
    Do not change the text in any way.
    Leave abbreviations exactly as they are.
    Use UTF-8 characters only. No MathML.
    If the data field is not found in the text return the default value.
    Do not add or delete any punctuation and do not add or delete any spaces.
    Do not hallucinate.
    """

    text = InputField()

    scientificName: str = OutputField(
        default="",
        desc=(
            "Scientific name or species given as a list of 'Genus species' names. "
            "Do not include subspecies or varieties and do not include author names. "
        ),
    )
    scientificNameAuthorship: str = OutputField(
        default="",
        desc=(
            "Scientific name authorship. There is often more than one author per "
            "scientific name. Authors may be abbreviated, sometimes as a single letter."
        ),
    )
    infraspecificEpithet: str = OutputField(
        default="",
        desc="Contains the subspecies or variety portion of the scientific name",
    )
    infraspecificNameAuthorship: str = OutputField(
        default="",
        desc="The author (authority) who coined the infraspecific name.",
    )
    family: str = OutputField(
        default="",
        desc="Taxonomic family",
    )
    associatedTaxa: str = OutputField(
        default="",
        desc="Was the specimen found near, around, or on another species",
    )
    recordNumber: str = OutputField(
        default="",
        desc=(
            "The number used to identify the specimen. The record number is often "
            "found just after the collectors' name (recorded by).",
        ),
    )
    recordedBy: str = OutputField(
        default="",
        desc="The person or people who collected the specimen",
    )
    verbatimEventDate: str = OutputField(
        default="",
        desc="When was the specimen collected",
    )
    identifiedBy: str = OutputField(
        default="",
        desc="Who identified or verified the species",
    )
    dateIdentified: str = OutputField(
        default="",
        desc="When was the specimen identified or verified?",
    )
    country: str = OutputField(
        default="",
        desc="The country where the specimen was collected",
    )
    stateProvince: str = OutputField(
        default="",
        desc="The state or province where the specimen was collected",
    )
    county: str = OutputField(
        default="",
        desc="The county where the specimen was collected",
    )
    municipality: str = OutputField(
        default="",
        desc="Collected from this municipality",
    )
    verbatimElevation: str = OutputField(
        default="",
        desc="The specimen was collected at this elevation or altitude",
    )
    elevationValues: list[float] = OutputField(
        default=[],
        desc=(
            "The elevation values. More than one value could be an elevation range "
            "or it could be the same elevation reported in different units."
        ),
    )
    elevationUnits: list[str] = OutputField(
        default=[],
        desc=(
            "The elevation units. There may be more than one units reported when the "
            "same value is reported in different units."
        ),
    )
    elevationEstimated: bool = OutputField(
        default=False,
        desc="Is this an estimated elevation?",
    )
    verbatimLatitude: str = OutputField(
        default="",
        desc="The specimen was collected at this latitude.",
    )
    verbatimLongitude: str = OutputField(
        default="",
        desc="The specimen was collected at this longitude.",
    )
    geodeticDatum: str = OutputField(
        default="",
        desc=(
            "What geodetic datum is the latitude, longitude, TRS, or UTM using "
            'Examples "NAD27", "NAD83", "WGS84"'
        ),
    )
    trs: str = OutputField(
        default="",
        desc=(
            "Township Range Section (TRS). There may be a quad (quadrangle) associated "
            "with the TRS. The quad may come before or after the other fields. "
            'Examples "Bodie Quadrangle; T4N R25E S36", "T41N R15E NW 1/4 S10"'
            '"T7S, R1W SE 1/4 sec. 33", "SW 1/4 sec. 34.", '
            '"T23N R14E se1/4 ne1/4 sec 12 Reconnaissance quad", '
            '"S27, T 48 N , R 7 W Mt. Diablo Mer.", '
            '"T.43.R.11W., south-east corner section 7"'
        ),
    )
    trsTownship: str = OutputField(
        default="",
        desc=(
            'The township portion of the TRS. It will look like: "T28N" or "T 32 N". '
            'The letter "T" followed by a few digits and then an "N" or "S" compass '
            "direction."
        ),
    )
    trsRange: str = OutputField(
        default="",
        desc=(
            'The range portion of the TRS. It will look like: "R23E" or "R 1 W". '
            'The letter "R" followed by a few digits and then an "E" or "W" compass '
            "direction."
        ),
    )
    trsSection: str = OutputField(
        default="",
        desc=(
            'The section portion of the TRS. Examples look like "1/4 S10", '
            '"se1/4 ne1/4  sec 12", "SE ¼ Section 17", "NW¼ of sec. 8", "section 18" '
            '"S8 (SE¼)", "south-east corner section 7"'
        ),
    )
    trsQuad: str = OutputField(
        default="",
        desc=(
            "The quad (quadrangle) portion of the TRS. It may be at the beginning or "
            'end of the TRS. Examples look like: "USGS Wahtoke 7 1/2 quad", '
            '"Yountville Quad", "Chicken Hawk Hill quadrangle", "Mt. Ingalls quad."'
        ),
    )
    utm: str = OutputField(
        default="",
        desc=(
            "Universal Transverse Mercator (UTM) "
            'Examples  "33T 500000 4649776", "Z12 N7874900 E768500", '
            '"11S 316745.14 3542301.90", "10 3756206N, 0769161E", '
            '"11S - 0484145E, 3741382N", "10S, 709280 E, 3913480 N"'
            '"Zone 11S; 3845372N 0729522E"'
        ),
    )
    utmNorthing: str = OutputField(
        default="",
        desc=(
            "The northing portion of the UTM. "
            'It is a number (possibly negative, or a decimal) followed by an "N". '
            'It will look like: "3845372N", '
            '"4057.6 N", "3968400 N", "N 4253279", "4N"'
        ),
    )
    utmEasting: str = OutputField(
        default="",
        desc=(
            "The easting portion of the UTM. "
            'It is a number (possibly negative, or a decimal) followed by an "E". '
            'Examples look like "E 642700", '
            '"509257E", "- 0484145E", "546936", "368.2 E", "6E"'
        ),
    )
    utmZone: str = OutputField(
        default="",
        desc=(
            'The zone portion of the UTM. It will look like: "10S", "11", "8N", '
            '"Zone 11S;", "NH", "16P", "LJ".'
        ),
    )
    locality: list[str] = OutputField(
        default=[],
        desc=(
            "Get the locality from input text string. "
            "There may be multiple phrases that describe the locality. "
            "Exclude the TRS, UTM, elevation, and county."
        ),
    )
    habitat: str = OutputField(
        default="",
        desc="Collected from this habitat or environment.",
    )
    flowersPresent: bool = OutputField(
        default=False,
        desc="Are there flowers on the plant?",
    )
    fruitPresent: bool = OutputField(
        default=False,
        desc="Is there fruit on the plant?",
    )
    flowerColor: str = OutputField(
        default="",
        desc="What are the colors of the flowers?",
    )
    fruitColor: str = OutputField(
        default="",
        desc="What are the colors of the fruits?",
    )
    plantHeight: str = OutputField(
        default="",
        desc="How tall is the specimen?",
    )
    plantSize: list[str] = OutputField(
        default=[],
        desc="Other specimen sizes?",
    )
    habit: str = OutputField(
        default="",
        desc=(
            "What is the specimen habit? "
            'Examples "herbaceous", "woody", "decumbent", "erect"'
        ),
    )
    abundance: str = OutputField(
        default="",
        desc=(
            'How common is the specimen? Examples include "common", "scattered", "rare"'
        ),
    )
    leafShape: str = OutputField(
        default="",
        desc=(
            "What is the shape of the specimen's leaf? "
            'Examples "acute", "caudate", "elliptic", "lobed"'
        ),
    )
    leafMargin: str = OutputField(
        default="",
        desc=(
            "Description of the specimen's leaf margins. "
            'Examples "entire", "crenate", "dentate", "serrate"'
        ),
    )
    occurrenceRemarks: list[str] = OutputField(
        default=[],
        desc="This contains all other observations not in the other fields",
    )
