with first_term as (
    select
        account_id,
        min(start_date) as cohort_start
    from {{ ref('stg_subscriptions') }}
    where term_number = 1
    group by 1
),

cohorted as (
    select
        date_trunc('month', f.cohort_start) as cohort_month,
        s.account_id,
        s.term_number,
        s.mrr,
        s.end_status
    from {{ ref('stg_subscriptions') }} s
    join first_term f
        on s.account_id = f.account_id
),

base as (
    select
        cohort_month,
        sum(mrr) as starting_mrr,
        count(distinct account_id) as starting_accounts
    from cohorted
    where term_number = 1
    group by 1
)

select
    c.cohort_month,
    c.term_number,
    b.starting_accounts,
    b.starting_mrr,
    count(distinct c.account_id) as accounts,
    sum(c.mrr) as mrr,
    round(100.0 * count(distinct c.account_id) / nullif(b.starting_accounts, 0), 1) as account_retention_pct,
    round(100.0 * sum(c.mrr) / nullif(b.starting_mrr, 0), 1) as net_revenue_retention_pct,
    round(100.0 * least(sum(c.mrr), b.starting_mrr) / nullif(b.starting_mrr, 0), 1) as gross_revenue_retention_pct
from cohorted c
join base b
    on c.cohort_month = b.cohort_month
group by 1, 2, 3, 4