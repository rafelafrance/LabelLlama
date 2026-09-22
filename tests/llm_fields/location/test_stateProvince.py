import unittest

from llama.llm_fields.location.stateProvince import StateProvince


class TestStateProvince(unittest.TestCase):
    def test_state_province_01(self) -> None:
        """Value present in the text is kept and title-cased."""
        assert StateProvince("collected in Texas", "texas").stateProvince == "Texas"

    def test_state_province_02(self) -> None:
        """A lower case name is title cased, small words left down."""
        assert (
            StateProvince(
                "Provincia de Buenos Aires", "provincia de buenos aires"
            ).stateProvince
            == "Provincia de Buenos Aires"
        )

    def test_state_province_04(self) -> None:
        """Value not present in the text is a hallucination and becomes empty."""
        assert StateProvince("in Texas", "New York").stateProvince == ""

    def test_state_province_05(self) -> None:
        """Empty text: everything is a hallucination."""
        assert StateProvince("", "Texas").stateProvince == ""

    def test_state_province_10(self) -> None:
        """A one character word in state/province is properly handled."""
        assert StateProvince("my x state", "my x state").stateProvince == "My X State"
