`lifeStage` (str):
Extract the developmental or phenological stage of the specimen.
This describes the current growth phase or maturity level of the plant
at the time of collection. It is distinct from life cycle
(annual/biennial/perennial) and from flowersPresent/fruitPresent booleans.

Developmental maturity: 'seedling', 'juvenile', 'immature', 'young',
'mature', 'adult', 'old', 'senescent', 'established', 'sapling',
'seed', 'propagule', 'tissue culture', 'ex vitro'.

Reproductive/phenological state: 'flowering', 'in flower', 'blooming',
'fruiting', 'in fruit', 'seeding', 'in seed', 'flower and fruit',
'fl. and fr.', 'flowering and fruiting', 'flowering and seeding'.

Seasonal/resting state: 'dormant', 'dormancy', 'resting', 'dormant
with buds', 'dormant with flower buds', 'dormant with fruit'.

If no life stage information is stated, return an empty string.
