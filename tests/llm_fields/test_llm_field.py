import inspect
import unittest
from dataclasses import dataclass, is_dataclass

from llama.llm_fields.llm_field import LlmField


def make_sample(**fields: str) -> type[LlmField]:
    """Minimal concrete subclass used to exercise the base class."""
    namespace = {"__annotations__": dict.fromkeys(fields, str)}
    namespace.update(fields)
    return dataclass(type("SampleLlm", (LlmField,), namespace))


SampleLlm = make_sample(beta="")


class TestLlmField(unittest.TestCase):
    def test_llm_field_01(self) -> None:
        """LlmField is a dataclass so subclasses can inherit from it."""
        assert is_dataclass(LlmField)

    def test_llm_field_02(self) -> None:
        """Subclasses construct as (text, **field_values)."""
        field = SampleLlm("hello", "x")
        assert field.beta == "x"

    def test_llm_field_03(self) -> None:
        """Text is the first init parameter (an InitVar)."""
        params = list(inspect.signature(LlmField).parameters)
        assert params[0] == "text"

    def test_llm_field_04(self) -> None:
        """Get_field_names returns the (stored) field names of a subclass."""
        assert SampleLlm.get_field_names() == ["beta"]

    def test_llm_field_05(self) -> None:
        """ClassVars (scoring_method) are not reported as fields."""
        assert "scoring_method" not in SampleLlm.get_field_names()

    def test_llm_field_06(self) -> None:
        """The default scoring method for LLM fields is LR."""
        assert LlmField.scoring_method == "LR"

    def test_llm_field_07(self) -> None:
        """Identical values score a perfect one."""
        assert LlmField.score("abc", "abc", {}) == 1.0

    def test_llm_field_08(self) -> None:
        """Score: surrounding whitespace is ignored."""
        assert LlmField.score(" abc ", "abc", {}) == 1.0

    def test_llm_field_09(self) -> None:
        """Score: values are stringified before comparison."""
        assert LlmField.score(1.5, "1.5", {}) == 1.0

    def test_llm_field_10(self) -> None:
        """Score: empty expect vs non-empty actual."""
        assert LlmField.score("", "abc", {}) == 0.0

    def test_llm_field_11(self) -> None:
        """InitVar fields (like text) are not part of the field list."""
        assert LlmField.get_field_names() == []


if __name__ == "__main__":
    unittest.main()
