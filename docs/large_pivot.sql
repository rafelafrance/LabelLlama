copy (
  with piv as (
      with run as (select * from dwc where dwc_run_id = 7)
     pivot run on field using first(value) group by ocr_id
  )
  select ocr_text, ocr_id, image_path, scientificName, scientificNameAuthorship,
         infraspecificEpithet, infraspecificNameAuthorship, family, associatedTaxa,
         recordNumber, recordedBy, verbatimEventDate, identifiedBy, dateIdentified,
         country, stateProvince, county, municipality, verbatimElevation,
         elevationValues, elevationUnits, elevationEstimated, verbatimLatitude,
         verbatimLongitude, geodeticDatum, trs, township, range, section, quad,
         utm, northing, easting, zone, locality, habitat, flowersPresent, fruitPresent,
         flowerColor, fruitColor, plantHeight, plantSize, habit, abundance, leafShape,
         leafMargin, occurrenceRemarks
    from piv join ocr using (ocr_id)
) to 'data/herbarium/dwc_large_run_2026-03-06.csv';
