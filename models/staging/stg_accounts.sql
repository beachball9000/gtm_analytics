select
    account_id,
    account_name,
    segment,
    lower(trim(industry)) as industry,
    lower(trim(billing_state)) as billing_state,
    lower(trim(billing_region)) as billing_region,
    employee_Count,
    cast(created_date as date) as created_date
from {{ ref('raw_accounts') }}
{# from {{ ref('raw_accounts') }} #}