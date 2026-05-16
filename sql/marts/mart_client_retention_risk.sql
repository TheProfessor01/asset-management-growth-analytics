-- Client retention risk mart
-- Grain: one row per client.

create or replace view mart_client_retention_risk as
with latest_month as (
    select max(snapshot_month) as snapshot_month
    from monthly_asset_snapshots
),
latest_assets as (
    select
        mas.client_id,
        mas.advisor_id,
        sum(mas.ending_assets) as latest_assets
    from monthly_asset_snapshots mas
    join latest_month lm
        on mas.snapshot_month = lm.snapshot_month
    group by
        mas.client_id,
        mas.advisor_id
),
last_contact as (
    select
        client_id,
        max(activity_date) as last_contact_date,
        max(case when activity_type = 'Meeting' then activity_date end) as last_meeting_date
    from advisor_activities
    where client_id is not null
    group by client_id
),
recent_flows as (
    select
        mas.client_id,
        sum(mas.net_flows) as trailing_3_month_net_flows
    from monthly_asset_snapshots mas
    join latest_month lm
        on mas.snapshot_month >= lm.snapshot_month - interval '2 months'
    group by mas.client_id
)
select
    c.client_id,
    c.primary_advisor_id as advisor_id,
    a.advisor_name,
    a.team,
    a.region,
    c.client_segment,
    c.age_band,
    c.household_income_band,
    c.risk_tolerance,
    c.client_status,
    coalesce(la.latest_assets, 0) as latest_assets,
    lc.last_contact_date,
    lc.last_meeting_date,
    (select snapshot_month from latest_month) - lc.last_contact_date as days_since_last_contact,
    coalesce(rf.trailing_3_month_net_flows, 0) as trailing_3_month_net_flows,
    case
        when lc.last_contact_date is null then 1
        when (select snapshot_month from latest_month) - lc.last_contact_date > 120 then 1
        when coalesce(rf.trailing_3_month_net_flows, 0) < 0 then 1
        when c.client_segment = 'High Value'
             and (lc.last_meeting_date is null
                  or (select snapshot_month from latest_month) - lc.last_meeting_date > 180) then 1
        else 0
    end as at_risk_flag
from clients c
join advisors a
    on c.primary_advisor_id = a.advisor_id
left join latest_assets la
    on c.client_id = la.client_id
left join last_contact lc
    on c.client_id = lc.client_id
left join recent_flows rf
    on c.client_id = rf.client_id;

