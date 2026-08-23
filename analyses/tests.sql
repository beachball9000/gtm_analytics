select string_agg(column_name, E',\n    ' order by ordinal_position) as cols
from information_schema.columns
where table_name = 'raw_leads';


{# raw_contacts distinct count #}
{# select count(*) as total,
       count(distinct contact_id) as distinct_ids,
       count(distinct lower(trim(email))) as distinct_emails
from raw_contacts; #}