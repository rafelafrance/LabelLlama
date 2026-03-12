with dwc1 as (
  with run1 as (
    select ocr_id, field, value from dwc where dwc_run_id = 7 and field = 'scientificName'
  ) pivot run1 on field using first(value) group by ocr_id
),
gold1 as (
  with run2 as (
    select ocr_id, field, value from gold where gold_run_id = 2 and field = 'scientificName'
  ) pivot run2 on field using first(value) group by ocr_id)
select columns(dwc1.*) as "dwc1_\0", columns(gold1.*) as "gold_\0"
  from dwc1 join gold1 using (ocr_id);
