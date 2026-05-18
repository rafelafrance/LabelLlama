import unittest

from llama.pylib import fix_values


class TestPromptUtil(unittest.TestCase):
    # ---------------------------------------------------------------------
    def test_to_str_01(self) -> None:
        assert fix_values.to_str("test") == "test"
