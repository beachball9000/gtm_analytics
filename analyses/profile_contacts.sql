
{# SELECT 
    lower(trim(first_name)) as first_name,
    lower(trim(last_name)) as last_name,
    lower(trim(email)) as email,
    phone, 
    lower(trim(title)) as title,
    cast(created_date as date) as created_date
FROM {{ ref('raw_contacts') }} #}