select
    a.account_id,
    a.account_name,
    a.segment,
    a.industry,
    a.billing_state,
    a.billing_region,
    a.employee_count,
    a.created_date as account_created_date,
    min(s.start_date) as first_subscription_date,
    max(s.term_number) as terms_completed,
    count(s.subscription_id) as subscription_count,
    max(case when s.end_status = 'Churned' then 1 else 0 end) = 1 as has_churned,
    min(s.start_date) is not null as is_customer

from {{ ref('stg_accounts') }} a
left join {{ ref('stg_subscriptions') }} s
on a.account_id = s.account_id 
group by 1,2,3,4,5,6,7, 8