select
    opportunity_id,
    account_id,
    source_lead_id,
    opportunity_name,
    opportunity_type,
    plan_tier,
    amount,
    stage_name,
    is_closed,
    is_won,
    cast(created_date as date) as created_date,
    cast(close_date as date) as close_date,
    owner_region
from {{ ref('raw_opportunities') }}