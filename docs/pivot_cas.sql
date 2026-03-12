with piv as (with run as (select * from dwc where dwc_run_id = 7)
pivot run on field using first(value) group by ocr_id)
select * from piv join ocr using (ocr_id)

