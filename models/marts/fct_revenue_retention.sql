with terms as (
    select * from {{ ref('int_subscription_terms') }}
),

cohort_base as (
    select
        cohort_month,
        count(distinct account_id) as starting_accounts,
        sum(account_starting_mrr) as starting_mrr
    from terms
    where term_number = 1
    group by 1
)

select
    t.cohort_month,
    t.term_number,
    b.starting_accounts,
    b.starting_mrr,
    count(distinct t.account_id) as accounts,
    sum(t.mrr) as mrr,
    sum(t.capped_mrr) as retained_mrr,
    least(sum(t.mrr), b.starting_mrr) as cohort_capped_mrr,

    round(100.0 * count(distinct t.account_id) / nullif(b.starting_accounts, 0), 1) as account_retention_pct,

    round(100.0 * sum(t.mrr) / nullif(b.starting_mrr, 0), 1) as net_revenue_retention_pct,

    round(100.0 * sum(t.capped_mrr) / nullif(b.starting_mrr, 0), 1) as gross_revenue_retention_pct,

    round(100.0 * least(sum(t.mrr), b.starting_mrr) / nullif(b.starting_mrr, 0), 1) as gross_revenue_retention_cohort_capped_pct
    
from terms t
join cohort_base b
    on t.cohort_month = b.cohort_month
group by 1, 2, 3, 4