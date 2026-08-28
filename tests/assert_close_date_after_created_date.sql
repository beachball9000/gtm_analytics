-- Opportunities should never close before they were created
-- Returns offending rows; test passes when 0 rows come back

{{ config(severity='warn') }}

select 
opportunity_id,
account_id
created_date, 
close_date,
{{ dbt.datediff('created_date', 'close_date', 'day') }} as days_diff
from {{ ref('stg_opportunities') }}

where close_date < created_date