`scientificNameAuthorship` (str):
Extract the authorship citation for the species-level scientific name.
This is the person(s) who originally described the species, e.g., 'L.',
'Smith & Jones', '(Bartlett) Fernald'. There may be multiple authors.
Authors are often abbreviated, sometimes to a single letter.
This author may include a publication year, include that.
Do not include infraspecific authorship — that has its own field.
If no authorship is stated, return an empty string.
