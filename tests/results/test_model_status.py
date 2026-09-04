from llama.results.model_status import ModelStatus, StatusCounts


def test_normalize_accepts_success_variants() -> None:
    assert ModelStatus.normalize("success") == ModelStatus.SUCCESS
    assert ModelStatus.normalize("SUCCESS") == ModelStatus.SUCCESS
    assert ModelStatus.normalize(ModelStatus.SUCCESS) == ModelStatus.SUCCESS


def test_normalize_accepts_error_variants() -> None:
    assert ModelStatus.normalize("error") == ModelStatus.ERROR
    assert ModelStatus.normalize("ERROR") == ModelStatus.ERROR
    assert ModelStatus.normalize(ModelStatus.ERROR) == ModelStatus.ERROR


def test_normalize_unknown_values() -> None:
    assert ModelStatus.normalize("") == ModelStatus.UNKNOWN
    assert ModelStatus.normalize(None) == ModelStatus.UNKNOWN
    assert ModelStatus.normalize("other") == ModelStatus.UNKNOWN


def test_is_success() -> None:
    assert ModelStatus.is_success("success") is True
    assert ModelStatus.is_success("SUCCESS") is True
    assert ModelStatus.is_success("error") is False
    assert ModelStatus.is_success("") is False


def test_status_counts_normalizes_counted_statuses() -> None:
    statuses = StatusCounts()

    assert statuses.count("SUCCESS") == ModelStatus.SUCCESS
    assert statuses.count("success") == ModelStatus.SUCCESS
    assert statuses.count("error") == ModelStatus.ERROR

    assert statuses[ModelStatus.SUCCESS] == 2
    assert statuses[ModelStatus.ERROR] == 1
    assert statuses.get("unknown") == 0
