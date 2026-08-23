SELECT 
    lead_id,
    lower(trim(first_name)) as first_name,
    lower(trim(last_name)) as last_name,
    lower(trim(email)) as email,
    lower(trim(company)) as company,
    lower(trim(lead_source)) as lead_source,
    lower(trim(lead_status)) as lead_status,
    is_mql,
    cast(created_date as date) as created_date,
    converted_account_id,
    cast(converted_date as date) as converted_date
FROM {{ ref('raw_leads') }}