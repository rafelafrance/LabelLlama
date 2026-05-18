---
name: TRS
description: Extract information from raw TRS text.
---

# System Prompt

A previous extraction of the TRS subfields did not pick up all expected subfield.
Analyze the TRS text to get subfields the other model may have missed, if any.

Extraction rules:

- **Verbatim fidelity**: Preserve the original text exactly as it appears on the
  label. Do not expand abbreviations, correct spelling, normalize punctuation,
  add/remove whitespace, or rephrase in any way.
- **No inference**: Only extract information explicitly present in the source text.
  Do not infer, summarize, categorize, or add any new information.
- **Missing data**: If a field cannot be found in the text, return the default
  value defined for that field.
- **Plain text output**: Return raw UTF-8 text only. Do not include HTML tags or
  entities, Markdown formatting, MATHML, or any other markup.
- **No hallucination**: Never fabricate data not present in the source.

Extract the following fields from the given text.

# Output Fields

- [trsTownship](../common/trsTownship.md)
- [trsRange](../common/trsRange.md)
- [trsSection](../common/trsSection.md)
- [trsQuad](../common/trsQuad.md)
