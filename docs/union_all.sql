with piv1 as (with run1 as (select * from dwc where dwc_run_id = 7) pivot run1 on field using first(value) group by ocr_id),
piv2 as (with run2 as (select * from gold where gold_run_id = 3) pivot run2 on field using first(value) group by ocr_id)
select 'dwc' as dataset, doc_text, ocr_id, image_path, scientificName, scientificNameAuthorship, infraspecificEpithet,
       infraspecificNameAuthorship, family, associatedTaxa, recordNumber, recordedBy, verbatimEventDate, identifiedBy,
       dateIdentified, country, stateProvince, county, municipality, verbatimElevation, geodeticDatum, verbatimLatitude,
       verbatimLongitude, trs, utm, locality, habitat, occurrenceRemarks
  from piv1 join ocr using (ocr_id)
union all
select 'gold' as dataset, doc_text, ocr_id, image_path, scientificName, scientificNameAuthorship, infraspecificEpithet,
       infraspecificNameAuthorship, family, associatedTaxa, recordNumber, recordedBy, verbatimEventDate, identifiedBy,
       dateIdentified, country, stateProvince, county, municipality, verbatimElevation, geodeticDatum, verbatimLatitude,
       verbatimLongitude,  trs, utm, locality, habitat, occurrenceRemarks
  from piv2 join ocr using (ocr_id)
order by ocr_id, dataset desc;
