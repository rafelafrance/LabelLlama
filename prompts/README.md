# Prompts

I use these Markdown files to generate prompts for various tasks.
None of these Markdown files are designed to stand on their own.
They are all modified in some way before being sent to the LLM.
See [llm_prompt.py](../llama/pylib/llm_prompt.py).

There are three types:

1. Simple prompts only have a `System Message` section. I just pull in the text below the `System Message` heading. See [ocr_v1.md](ocr_v1.md) for an example of this type of prompt.

2. `LLM Fields` prompts extend the `System Message`with a list of target fields links to include. See [herbarium_v2.md](herbarium_v2.md) for an example. It also may have a list of calculated fields.

   The list of field prompts get expanded with contents of the field prompt Markdown files when generating the full prompt to the LLM.

   Field lists have many overlapping fields like scientificName that gets reused all over the place.

   `LLM Fields` prompts are stored in the `fields` subdirectories directory.

   There is also an optional `Calculated Fields` section.
   These are fields that take in data from previously parsed data and generate a new field from that data. See [eventDate](../llama/calculated/event/eventDate.py) for an example.

3. Field prompts hold the individual field descriptions used in the prompts. It contains the data types and instructions to the LLM on how to recognize and process the target data. See [scientificName_v1.md](fields/taxon/scientificName_v1.md) for an example.

   The field prompts themselves are stored other subdirectories under the `fields` directory based upon their research domain or Darwin Core category.

   Field prompts are designed to be included in a larger prompt. I will rethink this if the need arises for them to be used individually.
