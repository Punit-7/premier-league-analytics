-- Fails if dim_date is not one row per day. Power BI refuses to mark a
-- gapped table as a date table, so catch it here instead of in the dialog.
-- A singular test, because an aggregate cannot go in expression_is_true's WHERE.

select count(*) as days, min(full_date) as first_day, max(full_date) as last_day
from {{ ref('dim_date') }}
having count(*) != date_diff('day', min(full_date), max(full_date)) + 1
