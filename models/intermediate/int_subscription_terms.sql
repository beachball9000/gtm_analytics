with subs as (
    select * from {{ ref('stg_subscriptions') }}
)
,

first_term as (

    select
    account_id,
    start_Date as cohort_start,
    mrr as account_starting_mrr
    from subs
    where term_number = 1
)

select 
s.account_id,
s.subscription_id,
s.term_number,
date_trunc('month', f.cohort_start) as cohort_month,
f.cohort_start,
s.start_Date,
s.end_Date,
s.end_status,
s.plan_tier,
s.mrr,
f.account_starting_mrr,
least(s.mrr, f.account_starting_mrr) as capped_mrr
from subs s
join first_term f
on s.account_id = f.account_id