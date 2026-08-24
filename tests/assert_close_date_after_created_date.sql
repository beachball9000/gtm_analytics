-- Opportunities should never close before they were created
-- Returns offending rows; test passes when 0 rows come back

{{ config(severity='warn') }}

select 
opportunity_id,
account_id
created_date, 
close_date,
date_diff('day', created_date, close_date) as days_diff
from {{ ref('stg_opportunities') }}

where close_date < created_date