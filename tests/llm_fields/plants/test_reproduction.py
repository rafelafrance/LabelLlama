import unittest

from llama.llm_fields.plants.reproduction import Reproduction


class TestReproduction(unittest.TestCase):
    def test_reproduction_01(self) -> None:
        """A value present in the text is kept."""
        assert Reproduction(
            "the species is hermaphrodite", "hermaphrodite"
        ).reproduction == ("hermaphrodite")

    def test_reproduction_02(self) -> None:
        """Matching is case-insensitive; the value keeps its own casing."""
        assert (
            Reproduction("a DIOECIOUS plant", "dioecious").reproduction == "dioecious"
        )

    def test_reproduction_03(self) -> None:
        """A value not present in the text is a hallucination and becomes empty."""
        assert (
            Reproduction("the species is hermaphrodite", "monoecious").reproduction
            == ""
        )

    def test_reproduction_04(self) -> None:
        """An empty value stays empty."""
        assert Reproduction("some text", "").reproduction == ""
