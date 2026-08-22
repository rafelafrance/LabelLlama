from llama.llm_fields.event.habitat import Habitat
from llama.llm_fields.event.verbatimEventDate import VerbatimEventDate
from llama.llm_fields.identification.dateIdentified import DateIdentified
from llama.llm_fields.insects.lifeStage import LifeStage as InsectLifeStage
from llama.llm_fields.location.county import County
from llama.llm_fields.location.decimalLatitude import DecimalLatitude
from llama.llm_fields.location.decimalLongitude import DecimalLongitude
from llama.llm_fields.occurrence.associatedTaxa import AssociatedTaxa
from llama.llm_fields.occurrence.recordNumber import RecordNumber
from llama.llm_fields.occurrence.sex import Sex
from llama.llm_fields.taxon.genus import Genus
from llama.llm_fields.taxon.scientificName import ScientificName
from llama.llm_fields.taxon.specificEpithet import SpecificEpithet


def test_scientific_name_keeps_only_genus_and_species() -> None:
    field = ScientificName(scientificName="LIBELLULA LUCTUOSA (Burmeister, 1839)")
    assert field.scientificName == "Libellula luctuosa"


def test_genus_and_specific_epithet_normalize_case() -> None:
    assert Genus(genus="salix").genus == "Salix"
    assert SpecificEpithet(specificEpithet="ALBA").specificEpithet == "alba"


def test_sex_symbols_and_pair_are_normalized() -> None:
    assert Sex(sex="♂").sex == "male"
    assert Sex(sex="♀").sex == "female"
    assert Sex(sex="pair").sex == "male & female"


def test_decimal_coordinates_keep_numbers_and_clear_invalid_values() -> None:
    assert DecimalLatitude(decimalLatitude="45.5").decimalLatitude == 45.5
    assert DecimalLatitude(decimalLatitude="not a coordinate").decimalLatitude == ""
    assert DecimalLongitude(decimalLongitude="-120.25").decimalLongitude == -120.25
    assert DecimalLongitude(decimalLongitude="not a coordinate").decimalLongitude == ""


def test_common_label_prefixes_are_removed() -> None:
    assert RecordNumber(recordNumber="No. 123").recordNumber == "123"
    assert Habitat(habitat="Habitat: sphagnum bog").habitat == "sphagnum bog"
    assert VerbatimEventDate(verbatimEventDate="Date: 1999-05-01").verbatimEventDate
    assert DateIdentified(dateIdentified="date: 2020").dateIdentified == "2020"


def test_county_suffix_is_removed() -> None:
    assert County(county="Orange Co.").county == "Orange"
    assert County(county="Yolo County").county == "Yolo"


def test_associated_taxa_removes_markers_and_trailing_punctuation() -> None:
    field = AssociatedTaxa(associatedTaxa="*Quercus alba.")
    assert field.associatedTaxa == "Quercus alba"


def test_hallucinated_values_are_cleared_when_source_text_is_available() -> None:
    field = InsectLifeStage("adult label text", lifeStage="larva")
    assert field.lifeStage == ""


def test_hallucinated_values_are_kept_without_source_text() -> None:
    field = InsectLifeStage(lifeStage="larva")
    assert field.lifeStage == "larva"
