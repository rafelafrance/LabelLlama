from llama.llm_fields.location.decimalLongitude import DecimalLongitude


def test_decimal_longitude_01() -> None:
    assert DecimalLongitude("", "-1.0").decimalLongitude == -1.0
