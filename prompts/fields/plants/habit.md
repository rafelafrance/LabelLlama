`habit` (str): Extract the plant's habit or general growth form/shape. This describes the physical orientation, architecture, or overall shape of the plant's growth.

✅ Include:
- Growth orientation: 'erect', 'ascending', 'upright', 'semi-erect', 'decumbent', 'procumbent', 'prostrate', 'repent', 'humifuse'
- Growth architecture: 'creeping', 'climbing', 'twining', 'scandent', 'vine', 'liana', 'branching', 'lax', 'virgate'
- Growth form/shape: 'shrubby', 'arborescent', 'tree', 'bush', 'treelet', 'caespitose', 'cespitose', 'acaulescent', 'caulescent', 'fruticose'

❌ DO NOT include:
- Woodiness (stem tissue nature) — those belong in `woodiness` (e.g., 'woody', 'herbaceous', 'succulent', 'lignified')
- Ecological life form (nutritional strategy or substrate) — those belong in `lifeForm` (e.g., 'epiphytic', 'parasitic', 'aquatic', 'lithophytic')
- Life cycle or duration — those belong in `lifeCycle` (e.g., 'annual', 'biennial', 'perennial')
- Leaf shape or margin — those belong in `leafShape` and `leafMargin`
- Habitat or physical environment — those belong in `habitat` (e.g., 'forest', 'meadow', 'rocky slope')
- Abundance or frequency — those belong in `abundance` (e.g., 'common', 'rare')
- Labels or prefixes (e.g., 'habit:', 'growth form:') — extract only the habit term itself

Normalization: Return the term exactly as written on the label. Do not standardize synonyms (e.g., keep 'caespitose' or 'cespitose' as written). If multiple habit terms are listed, keep them as they appear.

Examples:
- 'erect' → 'erect'
- 'prostrate' → 'prostrate'
- 'climbing' → 'climbing'
- 'vine' → 'vine'
- 'caespitose' → 'caespitose'
- 'shrubby, erect' → 'shrubby, erect'
- 'woody' → '' (this is woodiness, not habit)
- 'herbaceous' → '' (this is woodiness, not habit)
- 'epiphytic' → '' (this is life form, not habit)
- 'annual' → '' (this is life cycle, not habit)
- 'in forest' → '' (this is habitat, not habit)
- 'common' → '' (this is abundance, not habit)

If no habit information is stated, return an empty string.
