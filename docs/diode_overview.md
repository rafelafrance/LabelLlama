## From 30,000 feet:
Extract information from labels on images of herbarium sheets.

There are 3 main steps:
1. OCR the text on the labels.
2. Extract information from the OCRed text.
3. Post-process the extracted text.

Of course things are a bit more complicated than just those 3 steps.

1. You supplied me with very crisp and clean images of models. The OCR engine (allenai/olmOCR-7B-0825) did a pretty good job of extracting the text. I made sure to also get the female and male symbols (♂ & ♀). I wasn't perfect, but as a first pass I am happy with the results.
2. Next I fed th OCRed text from step 1 into a small language model (ollama_chat/gemma3:27b) using modules that really help to limit hallucinations. All it has to do is recognize patterns in the text that correspond to Darwin Core fields. I wasn't sure which fields to target, so I made my best guess. Again, the results are not perfect, but they are an excellent starting point.
3. Post-processing of the data is the step that gets glossed over in all the tutorials, but it is every bit as important as the other 2 steps. It is also the one that requires the most input from the scientists using the data, so I really didn't do too much here. We still need to do things like:
   1. Convert the ♂ & ♀ symbols into text.
   2. Validate the output to make sure we are not getting hallucinations.
   3. Move certain data down into the dynamicProperties field.
   4. Convert verbatim data into its final form.
   5. Come up with a gold standard so that we can score the quality of the output.
   6. And more.

The details are in the notebooks/diode_trial_run.py marimo notebook. The repository is: https://github.com/rafelafrance/LabelLlama

Things are in heavy development, and I have several other information projects running at the same time.
