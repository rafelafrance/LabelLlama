---
name: ocr
description: OCR labels on images of museum specimens.
---

# Base Prompt

You are given an image of a museum specimen with labels.
I want you to extract all the text from every label and stamp on the specimen.
This includes text from both typewritten and handwritten labels.
It also includes text from stamps and smaller labels.
Ignore images, barcodes, QR-codes, rulers, and color test bars.
Ignore the specimen itself which is typically in the middle of the image.

- ✅ I want ALL the text.
- ✅ I only want the text without descriptions.
- ✅ I only want UTF-8 text without markup.
- ✅ I want the text EXACTLY as it is written.
- ❌ DO NOT describe images.
- ❌ DO NOT include HTML tags.
- ❌ DO NOT include Markdown tags.
- ❌ DO NOT include images.
- ❌ DO NOT hallucinate!
