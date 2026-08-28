{# select 
'dim_accounts' as model, 
count(*) from dim_accounts

union all 
select 
'fct_funnel_conversion', 
count(*) 
from fct_funnel_conversion


union all 
select 
'fct_revenue_retention', 
count(*) 
from fct_revenue_retention #}


select 
CAST(cohort_month AS DATE) as _cohort_month,
*
from fct_revenue_retention
{# where cohort_month = '2023-03-01' #}
order by _cohort_month DESC

{# select *
from int_opportunity_stage_transitions #}