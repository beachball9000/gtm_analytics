
{#   #}

with subs as (
    select * from {{ ref('stg_subscriptions') }}
)


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
