# Catalog of notebooks

Some of these are experiments while I try to find out what the best method is of
parsing labels.

## diode_trial_run.py

Extract Darwin Core information sent to me by the DiODE team.
This more or less worked, in that the DiODE team was able to use the output.

## georeference_diode.py

Labels on museum specimens often contain locality & administrative unit data.
This is an experiment to see if we can get a language model to extract that data.
I'm trying to go from raw text to decimal latitudes and longitudes.

## lightning_bug_trial_run.py

Test extracting label information from Lightning Bug images.
The wrinkle here is that the labels are from pinned specimens with multiple labels
on a pin.
Additionally, the specimen itself can obscure the image.
Their solution was to take images of the specimens from various angles, and try
to reconstruct the label from the multiple copies.
I OCRed all of the images from each angle and tried to find the "true" text of the
image by using multiple sequence alignment to get a consensus sequence.
I then ran the consensus sequence thru the language models.
I haven't heard back from the Lightning Bug team about the results.

## long_and_skinny.py

This was a one-off utility for comparing the results of various language models.
Super simple and kind of hard to interpret because there is no gold standard.

## skip_label_finder.py

Right now I am parsing herbarium labels in 3 steps:

1. Find the label on the herbarium sheet image & cut it out.
2. OCR the text of the labels.
3. Run the OCRed text thru a language model to extract useful information.

Obviously it would be great if we could reduce this down to a single step.
Doing that is, currently, not working well for herbarium sheets.
This is an attempt to remove step #1 the label finder and OCR all text from the sheet.
I am able to skip step #1 for dragonfly specimens, but they are not as noisy as
herbarium sheets.

## try_chandra_ocr.py

I am currently (2025-11-05) using OlmOCR as the main OCR engine for this project.
Of course every one is trying to out do the other teams and come up with new models.
The Chandra_OCR model scores better than OlmOCR on many tests.
I wanted to try this model, but it was not working on my machine.
I will return to this model (or another) in the future to see if there are improvements.
