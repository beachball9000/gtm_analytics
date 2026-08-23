with leads as (
    select
        date_trunc('month', created_date) as cohort_month,
        coalesce(nullif(lead_source, ''), 'unknown') as lead_source,
        count(*) as leads,
        sum(case when is_mql then 1 else 0 end) as mqls,
        sum(case when converted_account_id is not null then 1 else 0 end) as converted_leads
    from {{ ref('stg_leads') }}
    group by 1, 2
),

opps as (
    select
        date_trunc('month', l.created_date) as cohort_month,
        coalesce(nullif(l.lead_source, ''), 'unknown') as lead_source,
        count(distinct o.opportunity_id) as opportunities,
        count(distinct case when o.is_won then o.opportunity_id end) as closed_won,
        sum(case when o.is_won then o.amount else 0 end) as won_amount
    from {{ ref('stg_leads') }} l
    join {{ ref('stg_opportunities') }} o
        on l.lead_id = o.source_lead_id
    group by 1, 2
)

select
    l.cohort_month,
    l.lead_source,
    l.leads,
    l.mqls,
    l.converted_leads,
    coalesce(o.opportunities, 0) as opportunities,
    coalesce(o.closed_won, 0) as closed_won,
    coalesce(o.won_amount, 0) as won_amount,
    round(100.0 * l.mqls / nullif(l.leads, 0), 1) as lead_to_mql_pct,
    round(100.0 * coalesce(o.closed_won, 0) / nullif(l.leads, 0), 1) as lead_to_won_pct
from leads l
left join opps o
    on l.cohort_month = o.cohort_month
    and l.lead_source = o.lead_source