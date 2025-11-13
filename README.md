# Label Llama![CI](https://github.com/rafelafrance/LabelLlama/workflows/CI/badge.svg)

## From 30,000 feet:

Extract information from labels on images of herbarium sheets.

There are 2 main steps:

1. OCR the text on the images.
2. Extract information from the OCRed text.

Of course things are a bit more complicated than just those 2 steps.

### Given images of museum specimens

![Herbarium Sheet](assets/sheet.jpg)

### OCR text on the images

![OCRed Text](assets/show_ocr_text.png)

OCRed text from the label on the lower right of the sheet.

### Find text text in the labels

![text.png|Label Text](assets/text.png)

This is clearly from another sheet and label. The colors indicate text matched to fields.

### Output text to structured fields

![Label Traits](assets/traits.png)

The text is formatted and placed into named fields using the Darwin Core format.
