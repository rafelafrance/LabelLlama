import unittest

from llama.pylib import prompt_util


class TestPrompts(unittest.TestCase):
    def test_field_files_01(self) -> None:
        """All field modules have a corresponding prompt Markdown file."""
        modules = {prompt_util.normalize(f) for f in prompt_util.get_field_modules()}
        prompts = {prompt_util.normalize(p) for p in prompt_util.get_field_prompts()}
        assert modules == prompts

    def test_field_classes_02(self) -> None:
        """All field classes names match their field module name."""
        # Using lists because file stems & class names will repeat
        expect = [prompt_util.to_class_name(m) for m in prompt_util.get_field_modules()]
        actual = [cls.__name__ for cls in prompt_util.get_field_classes()]
        assert actual == expect

    def test_lm_prompts_03(self) -> None:
        """All LM prompt fields point to a real field prompt."""
        prompts = prompt_util.get_field_prompts()
        for lm_prompt in prompt_util.get_lm_prompts():
            sys_prompt, fields = prompt_util.read_lm_prompt(lm_prompt)
            assert len(sys_prompt) >= prompt_util.MIN_PROMPT_LEN
            for field in fields:
                prompt_path = prompt_util.to_prompt_path(field)
                assert prompt_path in prompts

    def test_field_prompt_prefix(self) -> None:
        for prompt_path in prompt_util.get_field_prompts():
            with prompt_path.open() as fin:
                prompt = fin.read()
            field_name = prompt_path.stem
            assert prompt.startswith(f"`{field_name}` ")
