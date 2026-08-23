select
    subscription_id,
    account_id,
    opportunity_id,
    plan_tier,
    mrr,
    term_number,
    cast(start_date as date) as start_date,
    cast(end_date as date) as end_date,
    end_status
from {{ ref('raw_subscriptions') }}