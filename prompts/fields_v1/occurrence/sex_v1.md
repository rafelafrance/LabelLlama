---
name: sex
description: Extract the biological sex of the specimen as recorded on the label. This describes the sex of the individual organism, distinct from life stage or morphological caste
module: llama/fields/occurrence/sex.py
---

# Prompt sex

`sex` (str): Extract the biological sex of the specimen as recorded on the label. This describes the sex of the individual organism, distinct from life stage or morphological caste.

✅ Include:
- Standard terms: 'male', 'female', 'hermaphrodite', 'intersex'
- Abbreviations and symbols: '♂', '♀', 'm', 'M', 'f', 'F', 'mal', 'fem', 'm.', 'f.'
- Combined or paired specimens: '♂♀', '♀♂', 'pair', '2m', '2f', 'mf', 'fm', 'male & female', 'male and female'
- Uncertain or undetermined: 'unknown', 'unsexed', 'sex unknown', 'unsexed specimen', '?♂', '?♀'
- Sex indicators in any position on the label (e.g., in header lines, after the species name, on collector notes)

❌ DO NOT include:
- Developmental/life stage: 'larva', 'pupa', 'nymph', 'imago', 'adult', 'juvenile'
- Social-insect castes: 'queen', 'worker', 'soldier', 'drone', 'dwarf male'
- Reproductive status: 'pregnant', 'oviparous', 'gravid', 'mated', 'virgin'
- Sex-linked morphological traits (e.g., 'with antennae', 'with mandibles') — extract only the sex designation

Normalization: Return the value exactly as written on the label — do not expand abbreviations or translate symbols. If no sex information is stated, return an empty string.
