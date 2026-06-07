# Prompts

I use these Markdown files to generate prompts for various tasks. None of these Markdown files are designed to stand on thier own. They are all modified in some way before being sent to the LLM. See [prompt_util.py](../llama/pylib/prompt_util.py).

There are three types:

1. Simple `System Prompts` only have a `System Prompt` section. I just pull in the text below the `System Prompt` heading. See [ocr.md](ocr.md) for an example of this type of prompt.

2. `Output Field` prompts extend `System Prompts`with a list of target fields links to include. See [herbarium.md](fields/herbarium.md) for an example. 
   
   The list of field prompts get expanded with contents of the field prompt Markdown files when generating the full prompt to the LLM.
   
   Field lists have many overlapping fields like scientificName that gets reused all over the place. 
   
   `Output Field` prompts are stored in the `fields` subdirectories directory.
   
   The expansion of the `Output Field`prompts (without the label text itself) can be a little over 26K characters which is less than 4K words long.

3. Field prompts hold the indiviual field descriptions used in the prompts. It contains the data types and instructions to the LLM on how to recognize and process the target data. See [scientificName.md](fields/taxon/scientificName.md) for an example. 
   
   The field prompts themselves are stored other subdirectories under the `fields` directory base upon their research domain or Darwin Core category.
   
   Field prompts are designed to be included in a larger prompt. I will rethink this if the need arises for them to be used individually.
