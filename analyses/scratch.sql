select 
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
from fct_revenue_retention
