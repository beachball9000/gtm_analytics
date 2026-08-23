select
    contact_id,
    account_id,
    first_name,
    last_name,
    lower(trim(email)) as email,
    title,
    cast(created_date as date) as created_date
from {{ ref('raw_contacts') }}
