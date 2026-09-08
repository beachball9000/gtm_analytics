with subs as (
    select * from {{ ref('stg_subscriptions') }}
)
,

first_term as (
select
    subs.account_id,
    subs.start_Date as cohort_start,
    subs.mrr as account_starting_mrr,
    sa.segment,
    sa.industry
    from subs
    join {{ ref('stg_accounts') }} sa
    on subs.account_id = sa.account_id
    where subs.term_number = 1
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
f.segment,
f.industry,
least(s.mrr, f.account_starting_mrr) as capped_mrr
from subs s
join first_term f
on s.account_id = f.account_id
