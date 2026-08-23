select count(*) as total,
       count(distinct contact_id) as distinct_ids,
       count(distinct lower(trim(email))) as distinct_emails
from raw_contacts;