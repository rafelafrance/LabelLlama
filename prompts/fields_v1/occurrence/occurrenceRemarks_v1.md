---
name: occurrenceRemarks
description: Extract any remaining observations, notes, or comments about the specimen occurrence that are not captured by other dedicated fields. This is a catch-all for data that does not fit elsewhere
module: llama/fields/occurrence/occurrenceRemarks.py
---

# Prompt occurrenceRemarks

`occurrenceRemarks` (str): Extract any remaining observations, notes, or comments about the specimen occurrence that are not captured by other dedicated fields. This is a catch-all for data that does not fit elsewhere.

✅ Include:
- Specimen condition or quality notes: 'damaged', 'wing missing', 'good condition', 'complete'
- Phenological or behavioral observations: 'in flight', 'feeding on nectar', 'mating pair'
- Collection circumstances or methods: 'collected at light trap', 'found under bark', 'reared from host'
- Color or morphological notes: 'forewings dark brown', 'red abdomen', 'large specimen'
- Preservation method or medium: '75% ethanol', 'pinned', 'spread specimen', 'on slide'
- Comments on identification quality or uncertainty: 'uncertain ID', 'similar to X. species', 'needs revision'
- Host or parasitoid relationships: 'parasitized by wasp', 'host: Drosophila melanogaster'
- Any other contextual information not covered by dedicated fields

❌ DO NOT include:
- Habitat descriptions — those belong in `habitat`
- Locality, coordinates, or administrative divisions — those belong in `locality`, coordinate fields, `country`, `stateProvince`, `county`, `municipality`
- Associated taxa or host plants — those belong in `associatedTaxa`
- Collector or determiner names — those belong in `recordedBy` or `identifiedBy`
- Dates or time information — those belong in `verbatimEventDate` or `dateIdentified`
- Elevation or altitude — those belong in `elevationValues` or `verbatimElevation`
- Scientific names, genus, species, or taxonomic data — those belong in `scientificName` and related fields
- Life stage — those belong in `lifeStage`
- Sex — those belong in `sex`
- Catalog numbers, record numbers, or institution codes — those belong in `catalogNumber`, `recordNumber`, `institutionCode`

Normalization: Preserve the text exactly as written — do not summarize, rephrase, or reorder notes. If multiple remarks are listed, include all of them. If no remarks are present, return an empty string.
