# Test processing Lightning Bug image

These are pinned insect museum specimens.
The specimen itself as well as other labels may obstruct the view of the labels.
In an attempt to see around the specimens, each label was imaged from several angles.

My part in this started after images were taken.
The image were already oriented and angle skewness corrected.
However, this does not mean that images were free of obstructions or 100% legible.
I tried to correct for this via the following method:

1. I grouped all images of the same label into a single batch.
2. I OCRed every image in the batch using the model allenai/olmOCR-7B-0825.
   1. Note this is no longer the preferred OCR model.
   2. Each OCR result is corrected for common OCR error
      like mistaking an "l" ell for a "1" one, etc.
   3. I also space normalized the text and other minor text adjustments.
3. I then ran an all-against-all Levenshtein distance for the entire batch of image.
I then threw out any OCR results that had a Levenshtein distance of 128.
    1. This step is more helpful for labels with more text.
4. I then performed a multiple sequence alignment (MSA) on all the remaining labels.
   1. The MSA is directly analogous to what researchers do for protein or DNA sequence.
      The difference is that I use a visual similarity matrix instead of a PAM250 matrix.
   2. Visual similarity is calculated by sliding each character/glyph over every
      other character. Because different fonts will yield different values I use
      stepped cutoff integer values from -2 to +2 inclusive.
5. The multiple sequence alignment is converted into a consensus sequence.
6. I put the consensus sequence through a model that I use for extracting
   Darwin Core fields google/gemma3:27b.
   1. I tried to limit model hallucinations by constraining the output formats,
      data types using DSPy.
   2. I also optimized the model prompt via training using "MIPROv2".
7. I reported the final Darwin Core fields along with the derived consensus sequence
   to collaborators.