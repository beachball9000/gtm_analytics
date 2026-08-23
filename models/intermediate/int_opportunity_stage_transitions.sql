select
    opportunity_id,
    min(case when stage_name = 'Prospecting' then entered_at end) as prospecting_at,
    min(case when stage_name = 'Discovery' then entered_at end) as discovery_at,
    min(case when stage_name = 'Demo' then entered_at end) as demo_at,
    min(case when stage_name = 'Proposal' then entered_at end) as proposal_at,
    min(case when stage_name = 'Negotiation' then entered_at end) as negotiation_at,
    min(case when stage_name = 'Closed Won' then entered_at end) as closed_won_at,
    min(case when stage_name = 'Closed Lost' then entered_at end) as closed_lost_at,
    count(*) as stage_touch_count
from {{ ref('stg_opportunity_stage_history') }}
group by 1