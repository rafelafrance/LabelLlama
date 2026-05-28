import unittest

from llama.pylib import prompt_util

MIN_PROMPT_LEN = 40


class TestPromptUtil(unittest.TestCase):
    def test_field_module_by_name_01(self) -> None:
        """
        Get the field module dict distinguishes modules with the same stem.

        Field modules are distinguished by what directory they are in. So,
        plants/sex != dwc/sex.
        """
        modules = prompt_util.field_modules_by_field_name()
        for key, module in modules.items():
            assert len(key.split("/")) == 2
            assert str(module).endswith(key + ".py")

    def test_field_prompts_by_name_02(self) -> None:
        """
        Get the field module dict distinguishes prompts with the same stem.

        Field prompts are distinguished by what directory they are in. So,
        plants/sex != dwc/sex.
        """
        prompts = prompt_util.field_prompts_by_field_name()
        for key, prompt in prompts.items():
            assert len(key.split("/")) == 2
            assert str(prompt).endswith(key + ".md")

    def test_field_classes_by_name_03(self) -> None:
        """
        Get the field module dict distinguishes prompts with the same stem.

        Field prompts are distinguished by what directory they are in. So,
        plants/sex != dwc/sex.
        """
        classes = prompt_util.field_classes_by_field_name()
        for key, cls in classes.items():
            assert len(key.split("/")) == 2
            assert key.endswith(prompt_util.field_class_to_column_name(cls))

