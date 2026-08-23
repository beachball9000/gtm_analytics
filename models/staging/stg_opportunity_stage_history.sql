select
    stage_history_id,
    opportunity_id,
    stage_name,
    cast(entered_at as date) as entered_at
from {{ ref('raw_opportunity_stage_history') }}