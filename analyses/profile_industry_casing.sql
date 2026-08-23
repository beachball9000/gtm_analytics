select count(distinct industry) as raw_distinct,
       count(distinct lower(trim(industry))) as cleaned_distinct
from raw_accounts;